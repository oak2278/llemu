"""
Tests for utility functions.
"""
import os
import tempfile
import pytest
from pathlib import Path

from llemu.utils import calculate_checksums, is_rom_file, parse_rom_name, create_standardized_name

def test_calculate_checksums():
    """Test calculating checksums for a file."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test data")
        file_path = f.name
        
    try:
        # Calculate checksums
        checksums = calculate_checksums(file_path)
        
        # Check results
        assert checksums['md5'] == 'eb733a00c0c9d336e65691a37ab54293'
        assert checksums['crc32'] == '028b4f5b'
        assert checksums['sha1'] == '7d70fe8e3fb4a1cde0bf968a19cc4bf2d5c78f40'
        assert checksums['size'] == 9
    finally:
        # Clean up
        os.unlink(file_path)
        
def test_is_rom_file():
    """Test checking if a file is a ROM."""
    # Test valid ROM extensions
    assert is_rom_file("game.nes") is True
    assert is_rom_file("game.smc") is True
    assert is_rom_file("game.gba") is True
    
    # Test invalid extensions
    assert is_rom_file("game.txt") is False
    assert is_rom_file("game.exe") is False
    assert is_rom_file("game") is False
    
def test_parse_rom_name():
    """Test parsing a ROM name into components."""
    # Test with region
    components = parse_rom_name("Super Mario Bros. (USA).nes")
    assert components['title'] == 'Super Mario Bros.'
    assert components['region'] == 'USA'
    assert components['version'] == ''
    assert components['attributes'] == []
    
    # Test with version
    components = parse_rom_name("Super Mario Bros. (v1.1).nes")
    assert components['title'] == 'Super Mario Bros.'
    assert components['region'] == ''
    assert components['version'] == '1.1'
    assert components['attributes'] == []
    
    # Test with attributes
    components = parse_rom_name("Super Mario Bros. [!].nes")
    assert components['title'] == 'Super Mario Bros.'
    assert components['region'] == ''
    assert components['version'] == ''
    assert components['attributes'] == ['!']
    
    # Test with all components
    components = parse_rom_name("Super Mario Bros. (USA) (v1.1) [!].nes")
    assert components['title'] == 'Super Mario Bros.'
    assert components['region'] == 'USA'
    assert components['version'] == '1.1'
    assert components['attributes'] == ['!']
    
def test_create_standardized_name():
    """Test creating a standardized ROM name."""
    # Test with all components
    components = {
        'title': 'Super Mario Bros.',
        'region': 'USA',
        'version': '1.1',
        'attributes': ['!']
    }
    name = create_standardized_name(components, '.nes')
    assert name == 'Super Mario Bros. (USA) (v1.1) [!].nes'
    
    # Test with missing components
    components = {
        'title': 'Super Mario Bros.',
        'region': '',
        'version': '',
        'attributes': []
    }
    name = create_standardized_name(components, '.nes')
    assert name == 'Super Mario Bros..nes'
