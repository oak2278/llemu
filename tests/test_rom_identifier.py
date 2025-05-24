"""
Tests for ROM identifier.
"""
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from llemu.rom_identifier import RomIdentifier
from llemu.database_manager import DatabaseManager

def test_identify_rom():
    """Test identifying a ROM."""
    # Create a mock database manager
    db_manager = MagicMock(spec=DatabaseManager)
    db_manager.find_rom_by_checksum.return_value = {
        'name': 'test_rom.nes',
        'description': 'Test ROM',
        'size': '131072',
        'md5': 'test_md5',
        'crc32': 'test_crc32',
        'sha1': 'test_sha1',
        'match_confidence': 1.0,
        'match_type': 'md5'
    }
    
    # Create ROM identifier
    identifier = RomIdentifier(db_manager)
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.nes', delete=False) as f:
        f.write(b"test data")
        file_path = f.name
        
    try:
        # Identify the ROM
        with patch('llemu.utils.calculate_checksums') as mock_checksums:
            mock_checksums.return_value = {
                'md5': 'test_md5',
                'crc32': 'test_crc32',
                'sha1': 'test_sha1',
                'size': 9
            }
            
            result = identifier.identify_rom(file_path)
            
        # Check results
        assert result['status'] == 'success'
        assert result['identified'] is True
        assert result['file_path'] == file_path
        assert result['file_name'] == os.path.basename(file_path)
        assert result['checksums']['md5'] == 'test_md5'
        assert result['rom_info']['name'] == 'test_rom.nes'
        assert result['match_confidence'] == 1.0
        assert result['match_type'] == 'md5'
        assert result['correct_name'] == 'test_rom.nes'
        assert result['name_matches'] is False  # Because the temp file name is different
        
        # Test with non-existent file
        result = identifier.identify_rom('nonexistent.nes')
        assert result['status'] == 'error'
        assert result['identified'] is False
        
        # Test with non-ROM file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"test data")
            non_rom_path = f.name
            
        result = identifier.identify_rom(non_rom_path)
        assert result['status'] == 'error'
        assert result['identified'] is False
        
        os.unlink(non_rom_path)
        
        # Test with unidentified ROM
        db_manager.find_rom_by_checksum.return_value = None
        
        result = identifier.identify_rom(file_path)
        assert result['status'] == 'success'
        assert result['identified'] is False
    finally:
        # Clean up
        os.unlink(file_path)
