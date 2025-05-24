"""
Tests for database manager.
"""
import os
import tempfile
import pytest
from pathlib import Path
import xml.etree.ElementTree as ET

from llemu.database_manager import DatabaseManager

def create_test_dat_file():
    """Create a test DAT file."""
    # Create a temporary file
    fd, file_path = tempfile.mkstemp(suffix='.dat')
    os.close(fd)
    
    # Create a simple DAT file
    root = ET.Element('datafile')
    
    header = ET.SubElement(root, 'header')
    name = ET.SubElement(header, 'name')
    name.text = 'Test Database'
    
    game1 = ET.SubElement(root, 'game', {'name': 'Game 1'})
    desc1 = ET.SubElement(game1, 'description')
    desc1.text = 'Game 1'
    rom1 = ET.SubElement(game1, 'rom', {
        'name': 'game1.nes',
        'size': '131072',
        'crc': 'abcd1234',
        'md5': '1a2b3c4d5e6f7g8h9i0j',
        'sha1': '1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t'
    })
    
    game2 = ET.SubElement(root, 'game', {'name': 'Game 2'})
    desc2 = ET.SubElement(game2, 'description')
    desc2.text = 'Game 2'
    rom2 = ET.SubElement(game2, 'rom', {
        'name': 'game2.nes',
        'size': '262144',
        'crc': 'efgh5678',
        'md5': '0j9i8h7g6f5e4d3c2b1a',
        'sha1': '0t9s8r7q6p5o4n3m2l1k0j9i8h7g6f5e4d3c2b1a'
    })
    
    # Write the DAT file
    tree = ET.ElementTree(root)
    tree.write(file_path)
    
    return file_path

def test_load_dat_file():
    """Test loading a DAT file."""
    # Create a test DAT file
    dat_file = create_test_dat_file()
    
    try:
        # Create database manager
        db_manager = DatabaseManager()
        
        # Load the DAT file
        success = db_manager.load_dat_file(dat_file)
        
        # Check results
        assert success is True
        assert 'Test Database' in db_manager.databases
        assert len(db_manager.databases['Test Database']['md5']) == 2
        assert '1a2b3c4d5e6f7g8h9i0j' in db_manager.databases['Test Database']['md5']
        assert '0j9i8h7g6f5e4d3c2b1a' in db_manager.databases['Test Database']['md5']
    finally:
        # Clean up
        os.unlink(dat_file)
        
def test_find_rom_by_checksum():
    """Test finding a ROM by checksum."""
    # Create a test DAT file
    dat_file = create_test_dat_file()
    
    try:
        # Create database manager
        db_manager = DatabaseManager()
        
        # Load the DAT file
        db_manager.load_dat_file(dat_file)
        
        # Find ROM by MD5
        rom_info = db_manager.find_rom_by_checksum({'md5': '1a2b3c4d5e6f7g8h9i0j'})
        
        # Check results
        assert rom_info is not None
        assert rom_info['name'] == 'game1.nes'
        assert rom_info['description'] == 'Game 1'
        assert rom_info['match_type'] == 'md5'
        assert rom_info['match_confidence'] == 1.0
        
        # Find ROM by CRC32
        rom_info = db_manager.find_rom_by_checksum({'crc32': 'efgh5678'})
        
        # Check results
        assert rom_info is not None
        assert rom_info['name'] == 'game2.nes'
        assert rom_info['description'] == 'Game 2'
        assert rom_info['match_type'] == 'crc32'
        assert rom_info['match_confidence'] == 0.95
        
        # Find ROM by SHA1
        rom_info = db_manager.find_rom_by_checksum({'sha1': '1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t'})
        
        # Check results
        assert rom_info is not None
        assert rom_info['name'] == 'game1.nes'
        assert rom_info['description'] == 'Game 1'
        assert rom_info['match_type'] == 'sha1'
        assert rom_info['match_confidence'] == 0.99
        
        # Test with non-existent checksum
        rom_info = db_manager.find_rom_by_checksum({'md5': 'nonexistent'})
        assert rom_info is None
    finally:
        # Clean up
        os.unlink(dat_file)
        
def test_find_rom_by_name():
    """Test finding ROMs by name."""
    # Create a test DAT file
    dat_file = create_test_dat_file()
    
    try:
        # Create database manager
        db_manager = DatabaseManager()
        
        # Load the DAT file
        db_manager.load_dat_file(dat_file)
        
        # Find ROMs by name
        results = db_manager.find_rom_by_name('game1')
        
        # Check results
        assert len(results) == 1
        assert results[0]['name'] == 'game1.nes'
        assert results[0]['description'] == 'Game 1'
        assert results[0]['match_type'] == 'name'
        
        # Test with partial name
        results = db_manager.find_rom_by_name('game')
        
        # Check results
        assert len(results) == 2
        
        # Test with non-existent name
        results = db_manager.find_rom_by_name('nonexistent')
        assert len(results) == 0
    finally:
        # Clean up
        os.unlink(dat_file)
