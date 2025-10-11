"""
S3 Uploader for Bit-by-Bit Pipeline
Handles uploading pipeline data to AWS S3 buckets.
"""

import os
import boto3
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError

from src.utils.logger import get_logger
from src.utils.env_loader import EnvLoader


class S3Uploader:
    """
    S3 Uploader for pipeline data.
    
    Handles uploading entire run directories, individual files,
    and managing S3 paths based on environment and run_id.
    """
    
    def __init__(self, config_loader):
        self.config_loader = config_loader
        self.env_loader = EnvLoader()
        self.logger = get_logger()
        
        # Get environment and upload settings
        self.environment = self.env_loader.get_env_var('ENVIRONMENT', 'development')
        self.upload_to_aws = self.env_loader.get_env_var('UPLOAD_TO_AWS', 'true').lower() == 'true'
        
        # Get S3 configuration
        self.bucket_name = self._get_bucket_name()
        self.region = self.env_loader.get_env_var('AWS_DEFAULT_REGION', 'us-east-1')
        
        # Initialize S3 client
        self.s3_client = None
        if self.upload_to_aws:
            self.s3_client = self._create_s3_client()
    
    def _get_bucket_name(self) -> Optional[str]:
        """Get the appropriate bucket name for current environment."""
        if self.environment == 'development':
            return self.env_loader.get_env_var('AWS_S3_BUCKET_DEV')
        elif self.environment == 'production':
            return self.env_loader.get_env_var('AWS_S3_BUCKET_PROD')
        return None
    
    def _create_s3_client(self):
        """Create S3 client with proper credentials."""
        try:
            # Get AWS credentials
            aws_access_key = self.env_loader.get_env_var('AWS_ACCESS_KEY_ID')
            aws_secret_key = self.env_loader.get_env_var('AWS_SECRET_ACCESS_KEY')
            aws_profile = self.env_loader.get_env_var('AWS_PROFILE')
            
            # Clean up profile name
            if aws_profile:
                aws_profile = aws_profile.split('#')[0].strip()
                if aws_profile and aws_profile != "Leave empty if using access keys" and aws_profile != "":
                    session = boto3.Session(profile_name=aws_profile)
                    return session.client('s3', region_name=self.region)
            
            if aws_access_key and aws_secret_key:
                # Clear any existing AWS profile environment variables to avoid conflicts
                old_profile = os.environ.pop('AWS_PROFILE', None)
                old_default_profile = os.environ.pop('AWS_DEFAULT_PROFILE', None)
                
                try:
                    client = boto3.client(
                        's3',
                        aws_access_key_id=aws_access_key,
                        aws_secret_access_key=aws_secret_key,
                        region_name=self.region
                    )
                    return client
                finally:
                    # Restore environment variables
                    if old_profile:
                        os.environ['AWS_PROFILE'] = old_profile
                    if old_default_profile:
                        os.environ['AWS_DEFAULT_PROFILE'] = old_default_profile
            else:
                return boto3.client('s3', region_name=self.region)
                
        except NoCredentialsError:
            self.logger.error("No AWS credentials found")
            return None
        except Exception as e:
            self.logger.error(f"Failed to create S3 client: {e}")
            return None
    
    def upload_file(self, local_file_path: str, s3_key: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Upload a single file to S3.
        
        Args:
            local_file_path: Path to local file
            s3_key: S3 key (path) for the file
            metadata: Optional metadata to attach to the file
            
        Returns:
            Dictionary with upload result
        """
        if not self.upload_to_aws or not self.s3_client:
            return {
                'success': False,
                'error': 'Upload disabled or S3 client not available',
                'skipped': True
            }
        
        try:
            local_path = Path(local_file_path)
            if not local_path.exists():
                return {
                    'success': False,
                    'error': f'Local file not found: {local_file_path}'
                }
            
            # Prepare upload arguments
            upload_args = {
                'Bucket': self.bucket_name,
                'Key': s3_key,
                'Body': local_path.read_bytes()
            }
            
            # Add metadata if provided
            if metadata:
                upload_args['Metadata'] = {str(k): str(v) for k, v in metadata.items()}
            
            # Upload file
            self.logger.info(f"Uploading {local_file_path} to s3://{self.bucket_name}/{s3_key}")
            response = self.s3_client.put_object(**upload_args)
            
            return {
                'success': True,
                's3_key': s3_key,
                'bucket': self.bucket_name,
                'etag': response.get('ETag', ''),
                'size': local_path.stat().st_size
            }
            
        except ClientError as e:
            error_msg = f"S3 upload failed: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Unexpected error during upload: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def upload_directory(self, local_dir_path: str, s3_prefix: str, 
                        include_patterns: Optional[List[str]] = None,
                        exclude_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Upload entire directory to S3.
        
        Args:
            local_dir_path: Path to local directory
            s3_prefix: S3 prefix (folder) for the files
            include_patterns: File patterns to include (e.g., ['*.json', '*.log'])
            exclude_patterns: File patterns to exclude (e.g., ['*.tmp', '*.bak'])
            
        Returns:
            Dictionary with upload results
        """
        if not self.upload_to_aws or not self.s3_client:
            return {
                'success': False,
                'error': 'Upload disabled or S3 client not available',
                'skipped': True
            }
        
        try:
            local_dir = Path(local_dir_path)
            if not local_dir.exists() or not local_dir.is_dir():
                return {
                    'success': False,
                    'error': f'Local directory not found: {local_dir_path}'
                }
            
            # Find all files to upload
            files_to_upload = []
            for file_path in local_dir.rglob('*'):
                if file_path.is_file():
                    # Check include patterns
                    if include_patterns:
                        if not any(file_path.match(pattern) for pattern in include_patterns):
                            continue
                    
                    # Check exclude patterns
                    if exclude_patterns:
                        if any(file_path.match(pattern) for pattern in exclude_patterns):
                            continue
                    
                    files_to_upload.append(file_path)
            
            if not files_to_upload:
                return {
                    'success': True,
                    'files_uploaded': 0,
                    'message': 'No files found to upload'
                }
            
            # Upload files
            results = []
            successful_uploads = 0
            
            for file_path in files_to_upload:
                # Calculate relative path for S3 key
                relative_path = file_path.relative_to(local_dir)
                s3_key = f"{s3_prefix}/{relative_path}".replace('\\', '/')
                
                # Upload file
                result = self.upload_file(str(file_path), s3_key)
                results.append({
                    'file': str(file_path),
                    's3_key': s3_key,
                    'result': result
                })
                
                if result['success']:
                    successful_uploads += 1
            
            return {
                'success': successful_uploads > 0,
                'files_uploaded': successful_uploads,
                'total_files': len(files_to_upload),
                'results': results
            }
            
        except Exception as e:
            error_msg = f"Directory upload failed: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def upload_run_data(self, run_id: str) -> Dict[str, Any]:
        """
        Upload entire pipeline run data to S3.
        
        Args:
            run_id: Pipeline run identifier
            
        Returns:
            Dictionary with upload results
        """
        if not self.upload_to_aws or not self.s3_client:
            return {
                'success': False,
                'error': 'Upload disabled or S3 client not available',
                'skipped': True
            }
        
        try:
            # Get data paths
            data_paths = self.config_loader.get_data_paths()
            base_path = Path(data_paths['base'])
            
            if not base_path.exists():
                return {
                    'success': False,
                    'error': f'Run directory not found: {base_path}'
                }
            
            # Define S3 prefix for this run
            s3_prefix = f"runs/{run_id}"
            
            # Upload different data types
            upload_results = {}
            
            # Upload raw data
            raw_path = base_path / 'raw'
            if raw_path.exists():
                self.logger.info(f"Uploading raw data for run {run_id}")
                raw_result = self.upload_directory(
                    str(raw_path),
                    f"{s3_prefix}/raw",
                    include_patterns=['*.json', '*.csv', '*.txt']
                )
                upload_results['raw'] = raw_result
            
            # Upload processed data
            processed_path = base_path / 'processed'
            if processed_path.exists():
                self.logger.info(f"Uploading processed data for run {run_id}")
                processed_result = self.upload_directory(
                    str(processed_path),
                    f"{s3_prefix}/processed",
                    include_patterns=['*.json', '*.csv', '*.txt']
                )
                upload_results['processed'] = processed_result
            
            # Upload output data
            output_path = base_path / 'output'
            if output_path.exists():
                self.logger.info(f"Uploading output data for run {run_id}")
                output_result = self.upload_directory(
                    str(output_path),
                    f"{s3_prefix}/output",
                    include_patterns=['*.json', '*.csv', '*.txt', '*.html']
                )
                upload_results['output'] = output_result
            
            # Upload logs
            logs_path = base_path / 'logs'
            if logs_path.exists():
                self.logger.info(f"Uploading logs for run {run_id}")
                logs_result = self.upload_directory(
                    str(logs_path),
                    f"{s3_prefix}/logs",
                    include_patterns=['*.log', '*.txt']
                )
                upload_results['logs'] = logs_result
            
            # Create run metadata
            run_metadata = {
                'run_id': run_id,
                'environment': self.environment,
                'uploaded_at': datetime.now().isoformat(),
                'bucket': self.bucket_name,
                'upload_results': upload_results
            }
            
            # Upload run metadata
            metadata_key = f"{s3_prefix}/run_metadata.json"
            metadata_result = self.upload_file(
                'temp_metadata.json',
                metadata_key,
                {'content-type': 'application/json'}
            )
            
            # Clean up temp file
            if Path('temp_metadata.json').exists():
                Path('temp_metadata.json').unlink()
            
            # Calculate overall success
            total_files = sum(result.get('files_uploaded', 0) for result in upload_results.values())
            overall_success = total_files > 0
            
            return {
                'success': overall_success,
                'run_id': run_id,
                'environment': self.environment,
                'bucket': self.bucket_name,
                'total_files_uploaded': total_files,
                'upload_results': upload_results,
                'metadata_uploaded': metadata_result['success']
            }
            
        except Exception as e:
            error_msg = f"Run data upload failed: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def list_uploaded_runs(self) -> List[Dict[str, Any]]:
        """
        List all uploaded runs in S3.
        
        Returns:
            List of run information
        """
        if not self.upload_to_aws or not self.s3_client:
            return []
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='runs/',
                Delimiter='/'
            )
            
            runs = []
            for prefix in response.get('CommonPrefixes', []):
                run_id = prefix['Prefix'].rstrip('/').split('/')[-1]
                runs.append({
                    'run_id': run_id,
                    's3_prefix': prefix['Prefix']
                })
            
            return runs
            
        except Exception as e:
            self.logger.error(f"Failed to list uploaded runs: {e}")
            return []
    
    def get_upload_status(self) -> Dict[str, Any]:
        """
        Get current upload configuration status.
        
        Returns:
            Dictionary with upload status information
        """
        return {
            'upload_enabled': self.upload_to_aws,
            'environment': self.environment,
            'bucket_name': self.bucket_name,
            'region': self.region,
            's3_client_available': self.s3_client is not None
        }
