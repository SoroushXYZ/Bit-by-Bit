#!/usr/bin/env python3
"""
Newsletter Service for managing newsletter data operations.
Handles local newsletter data access and processing.
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime


class NewsletterService:
    """Service for managing newsletter data operations."""
    
    def __init__(self, local_data_dir: str = "data"):
        self.local_data_dir = local_data_dir
        
        # Ensure local data directory exists
        os.makedirs(self.local_data_dir, exist_ok=True)
    
    def get_available_dates(self) -> List[str]:
        """Get all available newsletter dates from local data folder."""
        try:
            if not os.path.exists(self.local_data_dir):
                return []
            
            dates = set()
            
            # Scan all run directories
            for item in os.listdir(self.local_data_dir):
                run_path = os.path.join(self.local_data_dir, item)
                if os.path.isdir(run_path):
                    # Extract date from folder name (format: YYYYMMDD_HHMMSS)
                    date_str = self._extract_date_from_folder_name(item)
                    if date_str:
                        dates.add(date_str)
            
            # Convert to sorted list (newest first)
            sorted_dates = sorted(list(dates), reverse=True)
            return sorted_dates
            
        except Exception as e:
            return []
    
    def _extract_date_from_folder_name(self, folder_name: str) -> Optional[str]:
        """Extract date from folder name in format YYYYMMDD_HHMMSS."""
        try:
            # Expected format: 20251013_155733
            if len(folder_name) == 15 and folder_name[8] == '_':
                date_part = folder_name[:8]  # YYYYMMDD
                time_part = folder_name[9:]  # HHMMSS
                
                # Validate date format
                year = int(date_part[:4])
                month = int(date_part[4:6])
                day = int(date_part[6:8])
                hour = int(time_part[:2])
                minute = int(time_part[2:4])
                second = int(time_part[4:6])
                
                # Basic validation
                if (1 <= month <= 12 and 1 <= day <= 31 and 
                    0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
                    
                    # Format as ISO date string for JavaScript
                    return f"{year}-{month:02d}-{day:02d}"
                
        except (ValueError, IndexError):
            pass
        
        return None
    
    def get_runs_for_date(self, date: str) -> List[Dict[str, Any]]:
        """Get all runs for a specific date (YYYY-MM-DD format)."""
        try:
            if not os.path.exists(self.local_data_dir):
                return []
            
            runs = []
            
            # Scan all run directories for the given date
            for item in os.listdir(self.local_data_dir):
                run_path = os.path.join(self.local_data_dir, item)
                if os.path.isdir(run_path):
                    # Extract date from folder name
                    folder_date = self._extract_date_from_folder_name(item)
                    if folder_date == date:
                        # Get run metadata
                        metadata_path = os.path.join(run_path, 'local_metadata.json')
                        metadata = None
                        if os.path.exists(metadata_path):
                            with open(metadata_path, 'r') as f:
                                metadata = json.load(f)
                        
                        runs.append({
                            'run_id': item,
                            'date': folder_date,
                            'path': run_path,
                            'metadata': metadata,
                            'last_modified': os.path.getmtime(run_path)
                        })
            
            # Sort by last modified (newest first)
            runs.sort(key=lambda x: x['last_modified'], reverse=True)
            return runs
            
        except Exception as e:
            return []
    
    def get_latest_run_for_date(self, date: str) -> Optional[Dict[str, Any]]:
        """Get the latest run for a specific date."""
        runs = self.get_runs_for_date(date)
        return runs[0] if runs else None
