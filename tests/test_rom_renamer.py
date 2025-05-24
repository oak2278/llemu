"""
Tests for ROM renamer.
"""
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from llemu.rom_renamer import RomRenamer
from llemu.rom_identifier import RomIdentifier

def test_generate_new_name():
    """Test generating a new name for a ROM."""
    # Create a mock identifier
    identifier = MagicMock(spec=RomIdentifier)
    
    # Create ROM renamer
    renamer = RomRenamer(identifier)
    
    # Test with name
    rom_info = {
        'name': 'test_rom.nes',
        'description': 'Test ROM'
    }
    
    new_name = renamer.generate_new_name(rom_info)
    assert new_name == 'test_rom.nes'
    
    # Test with description only
    rom_info = {
        'description': 'Test ROM',
        'file_path': 'test.nes'
    }
    
    new_name = renamer.generate_new_name(rom_info)
    assert new_name == 'Test ROM.nes'
    
    # Test with missing information
    rom_info = {}
    new_name = renamer.generate_new_name(rom_info)
    assert new_name is None
    
def test_rename_rom():
    """Test renaming a ROM."""
    # Create a mock identifier
    identifier = MagicMock(spec=RomIdentifier)
    identifier.identify_rom.return_value = {
        'status': 'success',
        'identified': True,
        'file_path': '/path/to/test.nes',
        'file_name': 'test.nes',
        'checksums': {
            'md5': 'test_md5',
            'crc32': 'test_crc32',
            'sha1': 'test_sha1',
            'size': 9
        },
        'rom_info': {
            'name': 'Super Mario Bros. (USA).nes',
            'description': 'Super Mario Bros. (USA)',
            'size': '131072',
            'md5': 'test_md5',
            'crc32': 'test_crc32',
            'sha1': 'test_sha1',
            'match_confidence': 1.0,
            'match_type': 'md5'
        },
        'match_confidence': 1.0,
        'match_type': 'md5',
        'correct_name': 'Super Mario Bros. (USA).nes',
        'name_matches': False
    }
    
    # Create ROM renamer
    renamer = RomRenamer(identifier)
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.nes', delete=False) as f:
        f.write(b"test data")
        file_path = f.name
        
    try:
        # Test dry run
        with patch('llemu.utils.safe_rename') as mock_rename:
            result = renamer.rename_rom(file_path, dry_run=True)
            
            # Check results
            assert result['status'] == 'success'
            assert result['renamed'] is True
            assert result['dry_run'] is True
            assert not mock_rename.called
            
        # Test actual rename
        with patch('llemu.utils.safe_rename') as mock_rename:
            mock_rename.return_value = True
            
            result = renamer.rename_rom(file_path)
            
            # Check results
            assert result['status'] == 'success'
            assert result['renamed'] is True
            assert result['new_name'] == 'Super Mario Bros. (USA).nes'
            assert mock_rename.called
            
        # Test with unidentified ROM
        identifier.identify_rom.return_value = {
            'status': 'success',
            'identified': False,
            'file_path': file_path,
            'file_name': os.path.basename(file_path)
        }
        
        result = renamer.rename_rom(file_path)
        
        # Check results
        assert result['status'] == 'error'
        assert result['renamed'] is False
        
        # Test with already correct name
        identifier.identify_rom.return_value = {
            'status': 'success',
            'identified': True,
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'rom_info': {
                'name': os.path.basename(file_path),
                'description': 'Test ROM'
            },
            'name_matches': True
        }
        
        result = renamer.rename_rom(file_path)
        
        # Check results
        assert result['status'] == 'success'
        assert result['renamed'] is False
        assert result['name_matches'] is True
    finally:
        # Clean up
        os.unlink(file_path)
