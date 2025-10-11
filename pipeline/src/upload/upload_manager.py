"""
Upload Manager for Bit-by-Bit Pipeline
Orchestrates S3 uploads and backend integration.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from src.utils.logger import get_logger
from src.utils.env_loader import EnvLoader
from .s3_uploader import S3Uploader


class UploadManager:
    """
    Manages uploads to S3 and backend API integration.
    
    Handles different upload strategies based on environment:
    - Local mode: Skip all uploads
    - Development: Upload to dev bucket + notify dev backend
    - Production: Upload to prod bucket + notify prod backend
    """
    
    def __init__(self, config_loader):
        self.config_loader = config_loader
        self.env_loader = EnvLoader()
        self.logger = get_logger()
        
        # Get environment settings
        self.environment = self.env_loader.get_env_var('ENVIRONMENT', 'development')
        self.upload_to_aws = self.env_loader.get_env_var('UPLOAD_TO_AWS', 'true').lower() == 'true'
        
        # Initialize S3 uploader
        self.s3_uploader = S3Uploader(config_loader)
        
        # Backend configuration
        self.backend_url = self._get_backend_url()
        self.backend_api_key = self.env_loader.get_env_var('BACKEND_API_KEY')
    
    def _get_backend_url(self) -> Optional[str]:
        """Get backend URL based on environment."""
        if self.environment == 'development':
            return self.env_loader.get_env_var('BACKEND_API_URL_DEV')
        elif self.environment == 'production':
            return self.env_loader.get_env_var('BACKEND_API_URL_PROD')
        return None
    
    def upload_run(self, run_id: str) -> Dict[str, Any]:
        """
        Upload entire pipeline run with backend notification.
        
        Args:
            run_id: Pipeline run identifier
            
        Returns:
            Dictionary with upload results
        """
        self.logger.info(f"🚀 Starting upload process for run {run_id}")
        
        # Check if upload is enabled
        if not self.upload_to_aws:
            self.logger.info("⏭️ Upload disabled (UPLOAD_TO_AWS=false)")
            return {
                'success': True,
                'skipped': True,
                'message': 'Upload disabled - running in local mode'
            }
        
        # Upload to S3
        s3_result = self.s3_uploader.upload_run_data(run_id)
        
        if not s3_result['success']:
            self.logger.error(f"❌ S3 upload failed: {s3_result.get('error')}")
            return {
                'success': False,
                'error': f"S3 upload failed: {s3_result.get('error')}",
                's3_result': s3_result
            }
        
        self.logger.info(f"✅ S3 upload completed: {s3_result.get('total_files_uploaded', 0)} files uploaded")
        
        # Notify backend
        backend_result = self._notify_backend(run_id, s3_result)
        
        # Combine results
        overall_success = s3_result['success'] and backend_result['success']
        
        return {
            'success': overall_success,
            'run_id': run_id,
            'environment': self.environment,
            's3_result': s3_result,
            'backend_result': backend_result,
            'uploaded_at': datetime.now().isoformat()
        }
    
    def _notify_backend(self, run_id: str, s3_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Notify backend about successful upload.
        
        Args:
            run_id: Pipeline run identifier
            s3_result: S3 upload results
            
        Returns:
            Dictionary with backend notification results
        """
        if not self.backend_url or not self.backend_api_key:
            self.logger.warning("⚠️ Backend URL or API key not configured - skipping backend notification")
            return {
                'success': True,
                'skipped': True,
                'message': 'Backend notification skipped - not configured'
            }
        
        try:
            # Prepare backend payload
            payload = {
                'run_id': run_id,
                'environment': self.environment,
                'uploaded_at': datetime.now().isoformat(),
                's3_bucket': s3_result.get('bucket'),
                'total_files': s3_result.get('total_files_uploaded', 0),
                'upload_results': s3_result.get('upload_results', {}),
                'metadata_uploaded': s3_result.get('metadata_uploaded', False)
            }
            
            # TODO: Implement actual backend API call
            # This is a placeholder for now
            self.logger.info(f"📡 Would notify backend at {self.backend_url}")
            self.logger.debug(f"Backend payload: {json.dumps(payload, indent=2)}")
            
            # For now, just return success
            return {
                'success': True,
                'backend_url': self.backend_url,
                'message': 'Backend notification (placeholder)'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Backend notification failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def upload_single_file(self, file_path: str, s3_key: str, 
                          metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Upload a single file to S3.
        
        Args:
            file_path: Path to local file
            s3_key: S3 key for the file
            metadata: Optional metadata
            
        Returns:
            Dictionary with upload results
        """
        return self.s3_uploader.upload_file(file_path, s3_key, metadata)
    
    def upload_directory(self, dir_path: str, s3_prefix: str,
                        include_patterns: Optional[list] = None,
                        exclude_patterns: Optional[list] = None) -> Dict[str, Any]:
        """
        Upload entire directory to S3.
        
        Args:
            dir_path: Path to local directory
            s3_prefix: S3 prefix for files
            include_patterns: File patterns to include
            exclude_patterns: File patterns to exclude
            
        Returns:
            Dictionary with upload results
        """
        return self.s3_uploader.upload_directory(
            dir_path, s3_prefix, include_patterns, exclude_patterns
        )
    
    def list_uploaded_runs(self) -> list:
        """
        List all uploaded runs.
        
        Returns:
            List of run information
        """
        return self.s3_uploader.list_uploaded_runs()
    
    def get_upload_status(self) -> Dict[str, Any]:
        """
        Get current upload configuration status.
        
        Returns:
            Dictionary with status information
        """
        s3_status = self.s3_uploader.get_upload_status()
        
        return {
            **s3_status,
            'backend_url': self.backend_url,
            'backend_configured': bool(self.backend_url and self.backend_api_key),
            'environment': self.environment
        }
    
    def validate_upload_setup(self) -> Dict[str, Any]:
        """
        Validate that upload setup is correct.
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'overall_success': True,
            'checks': {}
        }
        
        # Check upload enabled
        validation_results['checks']['upload_enabled'] = {
            'status': self.upload_to_aws,
            'message': 'Upload to AWS enabled' if self.upload_to_aws else 'Upload disabled'
        }
        
        if not self.upload_to_aws:
            validation_results['checks']['upload_enabled']['warning'] = 'Running in local mode'
            return validation_results
        
        # Check S3 client
        s3_status = self.s3_uploader.get_upload_status()
        validation_results['checks']['s3_client'] = {
            'status': s3_status['s3_client_available'],
            'message': 'S3 client available' if s3_status['s3_client_available'] else 'S3 client not available'
        }
        
        if not s3_status['s3_client_available']:
            validation_results['overall_success'] = False
        
        # Check bucket configuration
        validation_results['checks']['bucket_config'] = {
            'status': bool(s3_status['bucket_name']),
            'message': f"Bucket configured: {s3_status['bucket_name']}" if s3_status['bucket_name'] else 'No bucket configured'
        }
        
        if not s3_status['bucket_name']:
            validation_results['overall_success'] = False
        
        # Check backend configuration
        validation_results['checks']['backend_config'] = {
            'status': bool(self.backend_url and self.backend_api_key),
            'message': f"Backend configured: {self.backend_url}" if self.backend_url else 'Backend not configured'
        }
        
        if not self.backend_url:
            validation_results['checks']['backend_config']['warning'] = 'Backend notification will be skipped'
        
        return validation_results
