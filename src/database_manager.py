"""
Database manager for LLEMU.
Handles loading, parsing, and querying ROM databases.
"""
import os
import re
import xml.etree.ElementTree as ET
import json
import logging
from typing import Dict, List, Tuple, Optional, Union, Any
from pathlib import Path

from .utils import logger

class DatabaseManager:
    """
    Manages ROM databases for identification and verification.
    """
    
    def __init__(self, database_dir: str = None):
        """
        Initialize the database manager.
        
        Args:
            database_dir: Directory containing ROM databases
        """
        if database_dir is None:
            self.database_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        else:
            self.database_dir = database_dir
            
        self.databases = {}
        self.loaded_dats = set()
        
        # Create database directory if it doesn't exist
        os.makedirs(self.database_dir, exist_ok=True)
        
    def load_dat_file(self, dat_file: str) -> bool:
        """
        Load a DAT file into the database.
        
        Args:
            dat_file: Path to the DAT file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if already loaded
            if dat_file in self.loaded_dats:
                logger.info(f"DAT file {dat_file} already loaded")
                return True
                
            logger.info(f"Loading DAT file: {dat_file}")
            
            # Parse the DAT file
            tree = ET.parse(dat_file)
            root = tree.getroot()
            
            # Extract database name
            header = root.find('header')
            if header is not None:
                name = header.find('name')
                if name is not None:
                    db_name = name.text
                else:
                    db_name = os.path.basename(dat_file)
            else:
                db_name = os.path.basename(dat_file)
                
            # Initialize database if not exists
            if db_name not in self.databases:
                self.databases[db_name] = {
                    'md5': {},
                    'crc32': {},
                    'sha1': {},
                    'name': {}
                }
                
            # Process each game
            for game in root.findall('.//game'):
                game_name = game.get('name', '')
                description = game.find('description')
                if description is not None:
                    game_description = description.text
                else:
                    game_description = game_name
                    
                # Process each ROM
                for rom in game.findall('rom'):
                    rom_name = rom.get('name', '')
                    md5 = rom.get('md5', '').lower()
                    crc32 = rom.get('crc', '').lower()
                    sha1 = rom.get('sha1', '').lower()
                    size = rom.get('size', '0')
                    
                    # Add to database
                    if md5:
                        self.databases[db_name]['md5'][md5] = {
                            'name': rom_name,
                            'description': game_description,
                            'size': size,
                            'crc32': crc32,
                            'sha1': sha1
                        }
                        
                    if crc32:
                        self.databases[db_name]['crc32'][crc32] = {
                            'name': rom_name,
                            'description': game_description,
                            'size': size,
                            'md5': md5,
                            'sha1': sha1
                        }
                        
                    if sha1:
                        self.databases[db_name]['sha1'][sha1] = {
                            'name': rom_name,
                            'description': game_description,
                            'size': size,
                            'md5': md5,
                            'crc32': crc32
                        }
                        
                    # Add to name index
                    self.databases[db_name]['name'][rom_name] = {
                        'description': game_description,
                        'size': size,
                        'md5': md5,
                        'crc32': crc32,
                        'sha1': sha1
                    }
            
            # Mark as loaded
            self.loaded_dats.add(dat_file)
            logger.info(f"Loaded {len(self.databases[db_name]['md5'])} ROMs from {dat_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading DAT file {dat_file}: {e}")
            return False
            
    def load_all_dat_files(self) -> int:
        """
        Load all DAT files in the database directory.
        
        Returns:
            Number of DAT files loaded
        """
        count = 0
        for file in os.listdir(self.database_dir):
            if file.endswith('.dat') or file.endswith('.xml'):
                if self.load_dat_file(os.path.join(self.database_dir, file)):
                    count += 1
        return count
        
    def find_rom_by_checksum(self, checksums: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Find a ROM in the database by its checksums.
        
        Args:
            checksums: Dictionary containing the ROM checksums
            
        Returns:
            Dictionary containing the ROM information, or None if not found
        """
        md5 = checksums.get('md5', '').lower()
        crc32 = checksums.get('crc32', '').lower()
        sha1 = checksums.get('sha1', '').lower()
        size = checksums.get('size', 0)
        
        # Try to find by MD5 (most reliable)
        for db_name, db in self.databases.items():
            if md5 in db['md5']:
                result = db['md5'][md5].copy()
                result['database'] = db_name
                result['match_type'] = 'md5'
                result['match_confidence'] = 1.0  # 100% confidence
                return result
                
        # Try to find by SHA1
        for db_name, db in self.databases.items():
            if sha1 in db['sha1']:
                result = db['sha1'][sha1].copy()
                result['database'] = db_name
                result['match_type'] = 'sha1'
                result['match_confidence'] = 0.99  # 99% confidence
                return result
                
        # Try to find by CRC32
        for db_name, db in self.databases.items():
            if crc32 in db['crc32']:
                result = db['crc32'][crc32].copy()
                result['database'] = db_name
                result['match_type'] = 'crc32'
                result['match_confidence'] = 0.95  # 95% confidence
                return result
                
        # No match found
        return None
        
    def find_rom_by_name(self, name: str) -> List[Dict[str, Any]]:
        """
        Find ROMs in the database by name.
        
        Args:
            name: ROM name to search for
            
        Returns:
            List of dictionaries containing the ROM information
        """
        results = []
        
        # Normalize name for comparison
        normalized_name = name.lower()
        
        for db_name, db in self.databases.items():
            for rom_name, rom_info in db['name'].items():
                if normalized_name in rom_name.lower():
                    result = rom_info.copy()
                    result['name'] = rom_name
                    result['database'] = db_name
                    result['match_type'] = 'name'
                    
                    # Calculate confidence based on similarity
                    name_similarity = len(normalized_name) / max(len(normalized_name), len(rom_name.lower()))
                    result['match_confidence'] = min(0.8, name_similarity)  # Max 80% confidence for name matches
                    
                    results.append(result)
                    
        return sorted(results, key=lambda x: x['match_confidence'], reverse=True)
        
    def export_database_stats(self) -> Dict[str, Any]:
        """
        Export statistics about the loaded databases.
        
        Returns:
            Dictionary containing database statistics
        """
        stats = {
            'total_databases': len(self.databases),
            'total_roms': sum(len(db['md5']) for db in self.databases.values()),
            'databases': {}
        }
        
        for db_name, db in self.databases.items():
            stats['databases'][db_name] = {
                'roms': len(db['md5']),
                'unique_md5': len(db['md5']),
                'unique_crc32': len(db['crc32']),
                'unique_sha1': len(db['sha1'])
            }
            
        return stats
