"""
Utility functions for LLEMU.
"""
import os
import hashlib
import zlib
import logging
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'llemu.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('llemu')

def calculate_checksums(file_path: str) -> Dict[str, str]:
    """
    Calculate MD5, CRC32, and SHA1 checksums for a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary containing the checksums
    """
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            
        md5 = hashlib.md5(data).hexdigest()
        crc32 = format(zlib.crc32(data) & 0xFFFFFFFF, '08x')
        sha1 = hashlib.sha1(data).hexdigest()
        
        return {
            'md5': md5,
            'crc32': crc32,
            'sha1': sha1,
            'size': len(data)
        }
    except Exception as e:
        logger.error(f"Error calculating checksums for {file_path}: {e}")
        return {
            'md5': '',
            'crc32': '',
            'sha1': '',
            'size': 0
        }

def is_rom_file(file_path: str) -> bool:
    """
    Check if a file is a ROM based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file is a ROM, False otherwise
    """
    rom_extensions = [
        '.nes', '.smc', '.sfc', '.gb', '.gbc', '.gba', '.n64', '.z64', 
        '.v64', '.nds', '.iso', '.cue', '.bin', '.smd', '.md', '.32x',
        '.gg', '.sms', '.zip', '.7z', '.rom', '.ccd', '.chd'
    ]
    
    return os.path.splitext(file_path)[1].lower() in rom_extensions

def parse_rom_name(filename: str) -> Dict[str, str]:
    """
    Parse a ROM filename into its components.
    
    Args:
        filename: ROM filename
        
    Returns:
        Dictionary containing the parsed components
    """
    # Remove extension
    base_name = os.path.splitext(filename)[0]
    
    # Initialize components
    components = {
        'title': base_name,
        'region': '',
        'version': '',
        'attributes': []
    }
    
    # Extract region (in parentheses)
    region_match = re.search(r'\(([^)]+)\)', base_name)
    if region_match:
        components['region'] = region_match.group(1)
        
    # Extract version (in parentheses with 'v' prefix)
    version_match = re.search(r'\(v([^)]+)\)', base_name)
    if version_match:
        components['version'] = version_match.group(1)
        
    # Extract attributes (in square brackets)
    attributes_match = re.findall(r'\[([^\]]+)\]', base_name)
    if attributes_match:
        components['attributes'] = attributes_match
        
    # Clean up title (remove region, version, and attributes)
    title = base_name
    if region_match:
        title = title.replace(region_match.group(0), '')
    if version_match:
        title = title.replace(version_match.group(0), '')
    for attr in attributes_match:
        title = title.replace(f'[{attr}]', '')
    
    # Remove extra spaces and trim
    title = ' '.join(title.split())
    components['title'] = title
    
    return components

def create_standardized_name(components: Dict[str, str], extension: str) -> str:
    """
    Create a standardized ROM name from components.
    
    Args:
        components: Dictionary containing the ROM components
        extension: File extension
        
    Returns:
        Standardized ROM name
    """
    name = components['title']
    
    if components['region']:
        name += f" ({components['region']})"
        
    if components['version']:
        name += f" (v{components['version']})"
        
    for attr in components['attributes']:
        name += f" [{attr}]"
        
    return name + extension

def safe_rename(old_path: str, new_path: str, dry_run: bool = False) -> bool:
    """
    Safely rename a file, ensuring the destination directory exists.
    
    Args:
        old_path: Current file path
        new_path: New file path
        dry_run: If True, don't actually rename the file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if dry_run:
            logger.info(f"Would rename {old_path} to {new_path}")
            return True
            
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        
        # Rename the file
        os.rename(old_path, new_path)
        logger.info(f"Renamed {old_path} to {new_path}")
        return True
    except Exception as e:
        logger.error(f"Error renaming {old_path} to {new_path}: {e}")
        return False

def load_config() -> Dict[str, Any]:
    """
    Load configuration from the config file.
    
    Returns:
        Dictionary containing the configuration
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'settings.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return {}

def save_config(config: Dict[str, Any]) -> bool:
    """
    Save configuration to the config file.
    
    Args:
        config: Dictionary containing the configuration
        
    Returns:
        True if successful, False otherwise
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'settings.json')
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        return False

# Import re module for regex operations
import re
