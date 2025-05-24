#!/usr/bin/env python3
"""
Example usage of LLEMU.
"""
import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import llemu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llemu.database_manager import DatabaseManager
from llemu.rom_identifier import RomIdentifier
from llemu.rom_renamer import RomRenamer

def main():
    """
    Main function.
    """
    parser = argparse.ArgumentParser(description='LLEMU Example')
    parser.add_argument('--path', '-p', required=True, help='Path to ROMs directory')
    parser.add_argument('--dat', '-d', required=True, help='Path to DAT file')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (don\'t actually rename files)')
    args = parser.parse_args()
    
    # Initialize components
    db_manager = DatabaseManager()
    db_manager.load_dat_file(args.dat)
    
    identifier = RomIdentifier(db_manager)
    renamer = RomRenamer(identifier)
    
    # Identify and rename ROMs
    results = renamer.rename_roms_in_directory(args.path, recursive=True, dry_run=args.dry_run)
    
    # Generate report
    report = renamer.generate_renaming_report(results)
    
    # Print summary
    print(f"Scanned {report['total_roms']} ROMs")
    print(f"Identified {report['identified_roms']} ROMs ({report['identification_rate']:.1%})")
    print(f"{'Would rename' if args.dry_run else 'Renamed'} {report['renamed_roms']} ROMs")
    print(f"Already correct: {report['already_correct']} ROMs")
    
    # Print details of first 5 results
    print("\nFirst 5 results:")
    for i, result in enumerate(results[:5]):
        print(f"{i+1}. {result['file_path']}")
        print(f"   Identified: {result['identification']['identified']}")
        if result['identification']['identified']:
            print(f"   Match type: {result['identification']['match_type']}")
            print(f"   Confidence: {result['identification']['match_confidence']:.1%}")
            print(f"   Correct name: {result['new_name']}")
        print(f"   Renamed: {result['renamed']}")
        print()

if __name__ == '__main__':
    main()
