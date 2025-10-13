"""
S3 Service for fetching pipeline data from AWS S3.
"""

import os
import boto3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError


class S3Service:
    """Service for interacting with S3 bucket."""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.bucket_name = self._get_bucket_name()
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.s3_client = self._create_s3_client()
    
    def _get_bucket_name(self) -> str:
        """Get bucket name based on environment."""
        if self.environment == "production":
            return os.getenv("AWS_S3_BUCKET_PROD", "bit-by-bit-prod-data")
        return os.getenv("AWS_S3_BUCKET_DEV", "bit-by-bit-dev-data")
    
    def _create_s3_client(self):
        """Create S3 client with credentials."""
        try:
            aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            aws_profile = os.getenv("AWS_PROFILE")
            
            # Clean up profile name (remove comments and whitespace)
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
            raise Exception("AWS credentials not found")
        except Exception as e:
            raise Exception(f"Failed to create S3 client: {e}")
    
    def list_runs(self) -> List[Dict[str, Any]]:
        """List all pipeline runs in S3."""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='runs/',
                Delimiter='/'
            )
            
            runs = []
            for prefix in response.get('CommonPrefixes', []):
                if not prefix or 'Prefix' not in prefix:
                    continue
                    
                run_id = prefix['Prefix'].rstrip('/').split('/')[-1]
                if not run_id:
                    continue
                
                # Get run metadata if available
                metadata = self._get_run_metadata(run_id)
                
                # Debug: Check what files are actually in this run directory
                try:
                    files_response = self.s3_client.list_objects_v2(
                        Bucket=self.bucket_name,
                        Prefix=f"runs/{run_id}/"
                    )
                    actual_files = files_response.get('Contents', [])
                    file_count = len(actual_files)
                    file_names = [obj['Key'].split('/')[-1] for obj in actual_files]
                except:
                    file_count = 0
                    file_names = []
                
                runs.append({
                    'run_id': run_id,
                    's3_prefix': prefix['Prefix'],
                    'created_at': metadata.get('uploaded_at') if metadata else None,
                    'environment': metadata.get('environment') if metadata else 'unknown',
                    'total_files': metadata.get('upload_results', {}).get('total_files_uploaded', 0) if metadata else file_count,
                    'has_metadata': bool(metadata),
                    'debug_actual_files': file_count,
                    'debug_file_names': file_names[:10]  # Show first 10 files for debugging
                })
            
            # Sort by creation date (newest first)
            # Handle None values by using empty string as fallback
            runs.sort(key=lambda x: x.get('created_at') or '', reverse=True)
            return runs
            
        except ClientError as e:
            raise Exception(f"Failed to list runs: {e}")
        except Exception as e:
            raise Exception(f"Error listing runs: {e}")
    
    def get_run_data(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get data for a specific run."""
        try:
            # Get run metadata (optional)
            metadata = self._get_run_metadata(run_id)
            
            # Get all files in the run directory
            all_files = self._get_all_run_files(run_id)
            
            # Categorize files based on their names
            categorized_files = self._categorize_files(all_files)
            
            run_data = {
                'run_id': run_id,
                'metadata': metadata,
                'raw_data': categorized_files.get('raw', {'files': [], 'total_files': 0}),
                'processed_data': categorized_files.get('processed', {'files': [], 'total_files': 0}),
                'output_data': categorized_files.get('output', {'files': [], 'total_files': 0}),
                'logs': categorized_files.get('logs', {'files': [], 'total_files': 0}),
                'all_files': all_files
            }
            
            return run_data
            
        except Exception as e:
            raise Exception(f"Failed to get run data: {e}")
    
    def _get_all_run_files(self, run_id: str) -> List[Dict[str, Any]]:
        """Get all files in a run directory."""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"runs/{run_id}/"
            )
            
            files = []
            for obj in response.get('Contents', []):
                file_key = obj['Key']
                file_name = file_key.split('/')[-1]
                
                # Skip the run directory itself
                if file_name == run_id:
                    continue
                
                # Get file content for JSON files
                content = None
                if file_name.endswith('.json'):
                    try:
                        file_response = self.s3_client.get_object(
                            Bucket=self.bucket_name,
                            Key=file_key
                        )
                        content = json.loads(file_response['Body'].read().decode('utf-8'))
                    except:
                        content = None
                
                files.append({
                    'name': file_name,
                    'key': file_key,
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'content': content
                })
            
            return files
            
        except Exception as e:
            return []
    
    def _categorize_files(self, files: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Categorize files based on their S3 folder structure."""
        categories = {
            'raw': [],
            'processed': [],
            'output': [],
            'logs': []
        }
        
        for file_info in files:
            s3_key = file_info['key']
            
            # Extract folder from S3 key path: runs/{run_id}/{folder}/{filename}
            # Expected format: runs/20251013_155733/raw/file.json
            key_parts = s3_key.split('/')
            if len(key_parts) >= 3:
                folder_name = key_parts[2]  # This should be 'raw', 'processed', 'output', or 'logs'
                
                # Only categorize if it's one of our expected folders
                if folder_name in categories:
                    categories[folder_name].append(file_info)
                else:
                    # If folder doesn't match expected categories, put in processed as fallback
                    categories['processed'].append(file_info)
            else:
                # If key structure is unexpected, put in processed as fallback
                categories['processed'].append(file_info)
        
        # Convert to the expected format
        result = {}
        for category, file_list in categories.items():
            result[category] = {
                'folder': category,
                'files': file_list,
                'total_files': len(file_list)
            }
        
        return result
    
    def _get_run_metadata(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get run metadata from S3."""
        try:
            metadata_key = f"runs/{run_id}/run_metadata.json"
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=metadata_key
            )
            
            content = response['Body'].read().decode('utf-8')
            return json.loads(content)
            
        except ClientError:
            # Metadata file doesn't exist
            return None
        except Exception:
            return None
    
    def _get_folder_data(self, run_id: str, folder: str) -> Dict[str, Any]:
        """Get data from a specific folder (raw, processed, output, logs)."""
        try:
            folder_prefix = f"runs/{run_id}/{folder}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=folder_prefix
            )
            
            files = []
            for obj in response.get('Contents', []):
                file_key = obj['Key']
                file_name = file_key.split('/')[-1]
                
                # Get file content for JSON files
                content = None
                if file_name.endswith('.json'):
                    try:
                        file_response = self.s3_client.get_object(
                            Bucket=self.bucket_name,
                            Key=file_key
                        )
                        content = json.loads(file_response['Body'].read().decode('utf-8'))
                    except:
                        content = None
                
                files.append({
                    'name': file_name,
                    'key': file_key,
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'content': content
                })
            
            return {
                'folder': folder,
                'file_count': len(files),
                'files': files
            }
            
        except Exception as e:
            return {
                'folder': folder,
                'file_count': 0,
                'files': [],
                'error': str(e)
            }
    
    def sync_data(self) -> Dict[str, Any]:
        """Sync data from S3 bucket."""
        try:
            runs = self.list_runs()
            
            sync_result = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'environment': self.environment,
                'bucket': self.bucket_name,
                'total_runs': len(runs),
                'runs': runs
            }
            
            return sync_result
            
        except Exception as e:
            return {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_latest_run(self) -> Optional[Dict[str, Any]]:
        """Get the most recent pipeline run."""
        try:
            runs = self.list_runs()
            if not runs:
                return None
            
            latest_run_id = runs[0]['run_id']
            return self.get_run_data(latest_run_id)
            
        except Exception as e:
            raise Exception(f"Failed to get latest run: {e}")
    
    def get_run_summary(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a specific run without full data."""
        try:
            metadata = self._get_run_metadata(run_id)
            
            # Get all files and categorize them
            all_files = self._get_all_run_files(run_id)
            categorized_files = self._categorize_files(all_files)
            
            # Get file counts for each category
            folder_counts = {}
            for category in ['raw', 'processed', 'output', 'logs']:
                folder_counts[category] = categorized_files.get(category, {}).get('total_files', 0)
            
            return {
                'run_id': run_id,
                'created_at': metadata.get('uploaded_at') if metadata else None,
                'environment': metadata.get('environment') if metadata else 'unknown',
                'total_files': len(all_files),
                'folder_counts': folder_counts,
                'has_metadata': bool(metadata)
            }
            
        except Exception as e:
            return None
