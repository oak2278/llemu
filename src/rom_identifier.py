"""
ROM identifier for LLEMU.
Identifies ROMs based on checksums and database matching.
"""
import os
import logging
import json
from typing import Dict, List, Tuple, Optional, Union, Any
from pathlib import Path

from .utils import calculate_checksums, is_rom_file, logger
from .database_manager import DatabaseManager

class RomIdentifier:
    """
    Identifies ROMs based on checksums and database matching.
    """
    
    def __init__(self, database_manager: DatabaseManager = None):
        """
        Initialize the ROM identifier.
        
        Args:
            database_manager: Database manager instance
        """
        self.database_manager = database_manager or DatabaseManager()
        
    def identify_rom(self, file_path: str) -> Dict[str, Any]:
        """
        Identify a ROM file.
        
        Args:
            file_path: Path to the ROM file
            
        Returns:
            Dictionary containing the identification results
        """
        if not os.path.isfile(file_path):
            return {
                'status': 'error',
                'message': f"File not found: {file_path}",
                'file_path': file_path,
                'identified': False
            }
            
        if not is_rom_file(file_path):
            return {
                'status': 'error',
                'message': f"Not a ROM file: {file_path}",
                'file_path': file_path,
                'identified': False
            }
            
        # Calculate checksums
        checksums = calculate_checksums(file_path)
        
        # Find ROM in database
        rom_info = self.database_manager.find_rom_by_checksum(checksums)
        
        # Prepare result
        result = {
            'status': 'success',
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'checksums': checksums,
            'identified': rom_info is not None
        }
        
        if rom_info:
            result['rom_info'] = rom_info
            result['match_confidence'] = rom_info.get('match_confidence', 0.0)
            result['match_type'] = rom_info.get('match_type', 'unknown')
            result['correct_name'] = rom_info.get('name', '')
            
            # Check if current name matches correct name
            current_name = os.path.basename(file_path)
            correct_name = rom_info.get('name', '')
            
            result['name_matches'] = current_name == correct_name
            
        return result
        
    def identify_roms_in_directory(self, directory: str, recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Identify all ROMs in a directory.
        
        Args:
            directory: Directory containing ROMs
            recursive: Whether to search recursively
            
        Returns:
            List of dictionaries containing the identification results
        """
        results = []
        
        if not os.path.isdir(directory):
            logger.error(f"Directory not found: {directory}")
            return results
            
        # Walk through directory
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                
                if is_rom_file(file_path):
                    result = self.identify_rom(file_path)
                    results.append(result)
                    
            if not recursive:
                break
                
        return results
        
    def generate_identification_report(self, results: List[Dict[str, Any]], output_file: str = None) -> Dict[str, Any]:
        """
        Generate a report from identification results.
        
        Args:
            results: List of identification results
            output_file: Path to output file (optional)
            
        Returns:
            Dictionary containing the report
        """
        total_roms = len(results)
        identified_roms = sum(1 for r in results if r.get('identified', False))
        correct_names = sum(1 for r in results if r.get('name_matches', False))
        
        report = {
            'total_roms': total_roms,
            'identified_roms': identified_roms,
            'identification_rate': identified_roms / total_roms if total_roms > 0 else 0,
            'correct_names': correct_names,
            'correct_name_rate': correct_names / identified_roms if identified_roms > 0 else 0,
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
