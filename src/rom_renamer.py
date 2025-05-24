"""
ROM renamer for LLEMU.
Renames ROMs based on identification results.
"""
import os
import logging
import json
import shutil
from typing import Dict, List, Tuple, Optional, Union, Any
from pathlib import Path

from .utils import safe_rename, logger
from .rom_identifier import RomIdentifier
from .database_manager import DatabaseManager

class RomRenamer:
    """
    Renames ROMs based on identification results.
    """
    
    def __init__(self, identifier: RomIdentifier = None):
        """
        Initialize the ROM renamer.
        
        Args:
            identifier: ROM identifier instance
        """
        self.identifier = identifier or RomIdentifier()
        
    def generate_new_name(self, rom_info: Dict[str, Any]) -> str:
        """
        Generate a new name for a ROM based on its information.
        
        Args:
            rom_info: ROM information
            
        Returns:
            New name for the ROM
        """
        if 'name' in rom_info:
            return rom_info['name']
        elif 'description' in rom_info:
            # Convert description to filename
            name = rom_info['description']
            extension = os.path.splitext(rom_info.get('file_path', ''))[1]
            return f"{name}{extension}"
        else:
            return None
            
    def rename_rom(self, file_path: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Rename a ROM file based on identification.
        
        Args:
            file_path: Path to the ROM file
            dry_run: If True, don't actually rename the file
            
        Returns:
            Dictionary containing the renaming results
        """
        # Identify the ROM
        identification = self.identifier.identify_rom(file_path)
        
        if not identification.get('identified', False):
            return {
                'status': 'error',
                'message': f"Could not identify ROM: {file_path}",
                'file_path': file_path,
                'renamed': False,
                'identification': identification
            }
            
        # Generate new name
        rom_info = identification.get('rom_info', {})
        new_name = self.generate_new_name(rom_info)
        
        if not new_name:
            return {
                'status': 'error',
                'message': f"Could not generate new name for ROM: {file_path}",
                'file_path': file_path,
                'renamed': False,
                'identification': identification
            }
            
        # Check if name already matches
        current_name = os.path.basename(file_path)
        if current_name == new_name:
            return {
                'status': 'success',
                'message': f"ROM already has correct name: {file_path}",
                'file_path': file_path,
                'renamed': False,
                'identification': identification,
                'new_name': new_name,
                'name_matches': True
            }
            
        # Rename the file
        new_path = os.path.join(os.path.dirname(file_path), new_name)
        
        # Check if destination already exists
        if os.path.exists(new_path) and not dry_run:
            return {
                'status': 'error',
                'message': f"Destination file already exists: {new_path}",
                'file_path': file_path,
                'renamed': False,
                'identification': identification,
                'new_name': new_name,
                'new_path': new_path
            }
            
        # Perform the rename
        if dry_run:
            renamed = True
            logger.info(f"Would rename {file_path} to {new_path}")
        else:
            renamed = safe_rename(file_path, new_path)
            
        return {
            'status': 'success' if renamed else 'error',
            'message': f"{'Would rename' if dry_run else 'Renamed'} {file_path} to {new_path}" if renamed else f"Failed to rename {file_path}",
            'file_path': file_path,
            'renamed': renamed,
            'identification': identification,
            'new_name': new_name,
            'new_path': new_path,
            'dry_run': dry_run
        }
        
    def rename_roms_in_directory(self, directory: str, recursive: bool = True, dry_run: bool = False) -> List[Dict[str, Any]]:
        """
        Rename all ROMs in a directory.
        
        Args:
            directory: Directory containing ROMs
            recursive: Whether to search recursively
            dry_run: If True, don't actually rename the files
            
        Returns:
            List of dictionaries containing the renaming results
        """
        results = []
        
        # Identify all ROMs
        identifications = self.identifier.identify_roms_in_directory(directory, recursive)
        
        # Rename each ROM
        for identification in identifications:
            file_path = identification.get('file_path', '')
            if file_path:
                result = self.rename_rom(file_path, dry_run)
                results.append(result)
                
        return results
        
    def generate_renaming_report(self, results: List[Dict[str, Any]], output_file: str = None) -> Dict[str, Any]:
        """
        Generate a report from renaming results.
        
        Args:
            results: List of renaming results
            output_file: Path to output file (optional)
            
        Returns:
            Dictionary containing the report
        """
        total_roms = len(results)
        identified_roms = sum(1 for r in results if r.get('identification', {}).get('identified', False))
        renamed_roms = sum(1 for r in results if r.get('renamed', False))
        already_correct = sum(1 for r in results if r.get('name_matches', False))
        
        report = {
            'total_roms': total_roms,
            'identified_roms': identified_roms,
            'identification_rate': identified_roms / total_roms if total_roms > 0 else 0,
            'renamed_roms': renamed_roms,
            'already_correct': already_correct,
            'results': results
        }
        
        # Save report to file if specified
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(report, f, indent=4)
                logger.info(f"Report saved to {output_file}")
            except Exception as e:
                logger.error(f"Error saving report to {output_file}: {e}")
                
        return report
        
    def backup_roms(self, directory: str, backup_dir: str = None) -> bool:
        """
        Backup ROMs before renaming.
        
        Args:
            directory: Directory containing ROMs
            backup_dir: Directory to store backups (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if not backup_dir:
            backup_dir = f"{directory}_backup"
            
        try:
            # Create backup directory if it doesn't exist
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copy all files
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if is_rom_file(file):
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, directory)
                        dst_path = os.path.join(backup_dir, rel_path)
                        
                        # Create destination directory if it doesn't exist
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        
                        # Copy the file
                        shutil.copy2(src_path, dst_path)
                        
            logger.info(f"Backed up ROMs from {directory} to {backup_dir}")
            return True
        except Exception as e:
            logger.error(f"Error backing up ROMs: {e}")
            return False

# Import is_rom_file from utils
from .utils import is_rom_file
