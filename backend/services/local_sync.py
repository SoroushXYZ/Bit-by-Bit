#!/usr/bin/env python3
"""
Local data synchronization service.
Syncs data between S3 and local storage.
"""

import os
import json
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class LocalSyncService:
    """Service for syncing data between S3 and local storage."""
    
    def __init__(self, s3_service):
        self.s3_service = s3_service
        self.local_data_dir = "data"
        self.s3_client = s3_service.s3_client
        self.bucket_name = s3_service.bucket_name
        
        # Ensure local data directory exists
        os.makedirs(self.local_data_dir, exist_ok=True)
    
    def sync_all_runs(self) -> Dict[str, Any]:
        """Sync all runs between S3 and local storage."""
        try:
            # Get all runs from S3
            s3_runs = self.s3_service.list_runs()
            s3_run_ids = {run['run_id'] for run in s3_runs}
            
            # Get all local runs
            local_runs = self._get_local_runs()
            local_run_ids = {run['run_id'] for run in local_runs}
            
            # Find runs to download (in S3 but not local)
            runs_to_download = s3_run_ids - local_run_ids
            
            # Find runs to delete (local but not in S3)
            runs_to_delete = local_run_ids - s3_run_ids
            
            # Find runs to sync (in both, check if needs update)
            runs_to_sync = s3_run_ids & local_run_ids
            
            results = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                's3_runs': len(s3_runs),
                'local_runs': len(local_runs),
                'runs_to_download': list(runs_to_download),
                'runs_to_delete': list(runs_to_delete),
                'runs_to_sync': list(runs_to_sync),
                'download_results': [],
                'delete_results': [],
                'sync_results': []
            }
            
            # Download new runs
            for run_id in runs_to_download:
                result = self._download_run(run_id)
                results['download_results'].append(result)
            
            # Delete old runs
            for run_id in runs_to_delete:
                result = self._delete_local_run(run_id)
                results['delete_results'].append(result)
            
            # Sync existing runs (check if S3 is newer)
            for run_id in runs_to_sync:
                result = self._sync_run(run_id)
                results['sync_results'].append(result)
            
            return results
            
        except Exception as e:
            return {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _get_local_runs(self) -> List[Dict[str, Any]]:
        """Get list of local runs."""
        runs = []
        if not os.path.exists(self.local_data_dir):
            return runs
        
        for item in os.listdir(self.local_data_dir):
            run_path = os.path.join(self.local_data_dir, item)
            if os.path.isdir(run_path):
                runs.append({
                    'run_id': item,
                    'path': run_path,
                    'last_modified': os.path.getmtime(run_path)
                })
        
        return runs
    
    def _download_run(self, run_id: str) -> Dict[str, Any]:
        """Download a complete run from S3 to local storage with proper folder structure."""
        try:
            local_run_dir = os.path.join(self.local_data_dir, run_id)
            os.makedirs(local_run_dir, exist_ok=True)
            
            # Create folder structure
            folders = ['raw', 'processed', 'output', 'logs']
            for folder in folders:
                os.makedirs(os.path.join(local_run_dir, folder), exist_ok=True)
            
            # Get run data from S3 (this method works)
            try:
                run_data = self.s3_service.get_run_data(run_id)
                if not run_data:
                    return {
                        'run_id': run_id,
                        'status': 'error',
                        'error': 'No data found in S3 run'
                    }
                
                # Extract files from the run data
                all_files = run_data.get('all_files', [])
                if not all_files:
                    return {
                        'run_id': run_id,
                        'status': 'error',
                        'error': 'No files found in S3 run data'
                    }
                
                # Use the already categorized data
                categorized_files = {
                    'raw': run_data.get('raw_data', {}).get('files', []),
                    'processed': run_data.get('processed_data', {}).get('files', []),
                    'output': run_data.get('output_data', {}).get('files', []),
                    'logs': run_data.get('logs', {}).get('files', [])
                }
                
            except Exception as e:
                return {
                    'run_id': run_id,
                    'status': 'error',
                    'error': f'Failed to get run data from S3: {str(e)}'
                }
            downloaded_files = 0
            
            for category, file_list in categorized_files.items():
                for file_info in file_list:
                    # Determine local folder
                    if category == 'raw':
                        local_folder = 'raw'
                    elif category == 'processed':
                        local_folder = 'processed'
                    elif category == 'output':
                        local_folder = 'output'
                    elif category == 'logs':
                        local_folder = 'logs'
                    else:
                        local_folder = 'processed'  # default
                    
                    local_file_path = os.path.join(local_run_dir, local_folder, file_info['name'])
                    
                    # Download file from S3
                    self.s3_client.download_file(
                        self.bucket_name,
                        file_info['key'],
                        local_file_path
                    )
                    downloaded_files += 1
            
            # Save run metadata
            metadata = {
                'run_id': run_id,
                'downloaded_at': datetime.now().isoformat(),
                'total_files': downloaded_files,
                'source': 's3_sync',
                'folder_structure': {
                    'raw': len(categorized_files.get('raw', [])),
                    'processed': len(categorized_files.get('processed', [])),
                    'output': len(categorized_files.get('output', [])),
                    'logs': len(categorized_files.get('logs', []))
                }
            }
            
            metadata_path = os.path.join(local_run_dir, 'local_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return {
                'run_id': run_id,
                'status': 'downloaded',
                'files_downloaded': downloaded_files,
                'local_path': local_run_dir,
                'folder_structure': metadata['folder_structure']
            }
            
        except Exception as e:
            return {
                'run_id': run_id,
                'status': 'error',
                'error': str(e)
            }
    
    def _delete_local_run(self, run_id: str) -> Dict[str, Any]:
        """Delete a local run directory."""
        try:
            local_run_dir = os.path.join(self.local_data_dir, run_id)
            
            if os.path.exists(local_run_dir):
                shutil.rmtree(local_run_dir)
                return {
                    'run_id': run_id,
                    'status': 'deleted',
                    'local_path': local_run_dir
                }
            else:
                return {
                    'run_id': run_id,
                    'status': 'not_found',
                    'local_path': local_run_dir
                }
                
        except Exception as e:
            return {
                'run_id': run_id,
                'status': 'error',
                'error': str(e)
            }
    
    def _sync_run(self, run_id: str) -> Dict[str, Any]:
        """Sync an existing run (check if S3 is newer)."""
        try:
            # For now, just re-download to ensure sync
            # In the future, we could compare timestamps
            local_run_dir = os.path.join(self.local_data_dir, run_id)
            
            if os.path.exists(local_run_dir):
                # Remove existing local files
                shutil.rmtree(local_run_dir)
            
            # Download fresh from S3
            return self._download_run(run_id)
            
        except Exception as e:
            return {
                'run_id': run_id,
                'status': 'error',
                'error': str(e)
            }
    
    def get_local_run_data(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get data for a local run."""
        try:
            local_run_dir = os.path.join(self.local_data_dir, run_id)
            
            if not os.path.exists(local_run_dir):
                return None
            
            # Load local metadata
            metadata_path = os.path.join(local_run_dir, 'local_metadata.json')
            metadata = None
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
            
            # Get files from each folder
            categorized_files = {}
            all_files = []
            
            for folder in ['raw', 'processed', 'output', 'logs']:
                folder_path = os.path.join(local_run_dir, folder)
                folder_files = []
                
                if os.path.exists(folder_path):
                    for item in os.listdir(folder_path):
                        file_path = os.path.join(folder_path, item)
                        if os.path.isfile(file_path):
                            file_size = os.path.getsize(file_path)
                            file_mtime = os.path.getmtime(file_path)
                            
                            # Load content for JSON files
                            content = None
                            if item.endswith('.json'):
                                try:
                                    with open(file_path, 'r') as f:
                                        content = json.load(f)
                                except:
                                    content = None
                            
                            file_info = {
                                'name': item,
                                'path': file_path,
                                'size': file_size,
                                'last_modified': datetime.fromtimestamp(file_mtime).isoformat(),
                                'content': content
                            }
                            
                            folder_files.append(file_info)
                            all_files.append(file_info)
                
                categorized_files[folder] = {
                    'folder': folder,
                    'files': folder_files,
                    'total_files': len(folder_files)
                }
            
            return {
                'run_id': run_id,
                'metadata': metadata,
                'raw_data': categorized_files.get('raw', {'files': [], 'total_files': 0}),
                'processed_data': categorized_files.get('processed', {'files': [], 'total_files': 0}),
                'output_data': categorized_files.get('output', {'files': [], 'total_files': 0}),
                'logs': categorized_files.get('logs', {'files': [], 'total_files': 0}),
                'all_files': all_files,
                'local_path': local_run_dir
            }
            
        except Exception as e:
            return None
    
    def _categorize_files(self, files: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Categorize files based on their names (same as S3Service)."""
        categories = {
            'raw': [],
            'processed': [],
            'output': [],
            'logs': []
        }
        
        for file_info in files:
            file_name = file_info['name']
            
            # Categorize based on file name patterns
            if file_name.endswith('.log'):
                categories['logs'].append(file_info)
            elif any(pattern in file_name for pattern in ['rss_raw', 'github_trending', 'grid_blueprint']):
                categories['raw'].append(file_info)
            elif any(pattern in file_name for pattern in ['newsletter_output', 'filled_grid']):
                categories['output'].append(file_info)
            else:
                # Most other files are processed
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
