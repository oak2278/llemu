"""
Command-line interface for LLEMU.
"""
import os
import sys
import argparse
import json
import logging
from typing import Dict, List, Any

from .database_manager import DatabaseManager
from .rom_identifier import RomIdentifier
from .rom_renamer import RomRenamer
from .utils import logger

def main():
    """
    Main entry point for the command-line interface.
    """
    parser = argparse.ArgumentParser(description='LLEMU - LLM-Enhanced ROM Management Utility')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan ROMs for identification')
    scan_parser.add_argument('--path', '-p', required=True, help='Path to ROMs directory')
    scan_parser.add_argument('--recursive', '-r', action='store_true', help='Scan recursively')
    scan_parser.add_argument('--output', '-o', help='Output file for report')
    
    # Rename command
    rename_parser = subparsers.add_parser('rename', help='Rename ROMs based on identification')
    rename_parser.add_argument('--path', '-p', required=True, help='Path to ROMs directory')
    rename_parser.add_argument('--recursive', '-r', action='store_true', help='Scan recursively')
    rename_parser.add_argument('--dry-run', '-d', action='store_true', help='Dry run (don\'t actually rename files)')
    rename_parser.add_argument('--backup', '-b', action='store_true', help='Backup ROMs before renaming')
    rename_parser.add_argument('--output', '-o', help='Output file for report')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate a report from ROMs')
    report_parser.add_argument('--path', '-p', required=True, help='Path to ROMs directory')
    report_parser.add_argument('--recursive', '-r', action='store_true', help='Scan recursively')
    report_parser.add_argument('--output', '-o', required=True, help='Output file for report')
    report_parser.add_argument('--format', '-f', choices=['json', 'html', 'csv'], default='json', help='Report format')
    
    # Database command
    db_parser = subparsers.add_parser('db', help='Database management')
    db_parser.add_argument('--add', '-a', help='Add a DAT file to the database')
    db_parser.add_argument('--list', '-l', action='store_true', help='List loaded databases')
    db_parser.add_argument('--stats', '-s', action='store_true', help='Show database statistics')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize components
    db_manager = DatabaseManager()
    identifier = RomIdentifier(db_manager)
    renamer = RomRenamer(identifier)
    
    # Load databases
    db_count = db_manager.load_all_dat_files()
    logger.info(f"Loaded {db_count} DAT files")
    
    # Execute command
    if args.command == 'scan':
        results = identifier.identify_roms_in_directory(args.path, args.recursive)
        report = identifier.generate_identification_report(results, args.output)
        
        # Print summary
        print(f"Scanned {report['total_roms']} ROMs")
        print(f"Identified {report['identified_roms']} ROMs ({report['identification_rate']:.1%})")
        print(f"Correct names: {report['correct_names']} ({report['correct_name_rate']:.1%})")
        
    elif args.command == 'rename':
        # Backup if requested
        if args.backup:
            backup_dir = f"{args.path}_backup"
            print(f"Backing up ROMs to {backup_dir}...")
            renamer.backup_roms(args.path, backup_dir)
            
        # Rename ROMs
        results = renamer.rename_roms_in_directory(args.path, args.recursive, args.dry_run)
        report = renamer.generate_renaming_report(results, args.output)
        
        # Print summary
        print(f"Scanned {report['total_roms']} ROMs")
        print(f"Identified {report['identified_roms']} ROMs ({report['identification_rate']:.1%})")
        print(f"{'Would rename' if args.dry_run else 'Renamed'} {report['renamed_roms']} ROMs")
        print(f"Already correct: {report['already_correct']} ROMs")
        
    elif args.command == 'report':
        results = identifier.identify_roms_in_directory(args.path, args.recursive)
        
        if args.format == 'json':
            report = identifier.generate_identification_report(results, args.output)
            print(f"Report saved to {args.output}")
            
        elif args.format == 'html':
            # Generate HTML report
            html_report = generate_html_report(results)
            with open(args.output, 'w') as f:
                f.write(html_report)
            print(f"HTML report saved to {args.output}")
            
        elif args.format == 'csv':
            # Generate CSV report
            csv_report = generate_csv_report(results)
            with open(args.output, 'w') as f:
                f.write(csv_report)
            print(f"CSV report saved to {args.output}")
            
    elif args.command == 'db':
        if args.add:
            success = db_manager.load_dat_file(args.add)
            if success:
                print(f"Added DAT file: {args.add}")
            else:
                print(f"Failed to add DAT file: {args.add}")
                
        elif args.list:
            print("Loaded databases:")
            for db_name in db_manager.databases:
                print(f"- {db_name}")
                
        elif args.stats:
            stats = db_manager.export_database_stats()
            print(f"Total databases: {stats['total_databases']}")
            print(f"Total ROMs: {stats['total_roms']}")
            print("\nDatabase details:")
            for db_name, db_stats in stats['databases'].items():
                print(f"- {db_name}: {db_stats['roms']} ROMs")
                
    else:
        parser.print_help()

def generate_html_report(results: List[Dict[str, Any]]) -> str:
    """
    Generate an HTML report from identification results.
    
    Args:
        results: List of identification results
        
    Returns:
        HTML report as a string
    """
    total_roms = len(results)
    identified_roms = sum(1 for r in results if r.get('identified', False))
    correct_names = sum(1 for r in results if r.get('name_matches', False))
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>LLEMU ROM Identification Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .success {{ color: green; }}
        .error {{ color: red; }}
        .warning {{ color: orange; }}
        .summary {{ margin: 20px 0; padding: 10px; background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>LLEMU ROM Identification Report</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <p>Total ROMs: {total_roms}</p>
        <p>Identified ROMs: {identified_roms} ({identified_roms / total_roms:.1%})</p>
        <p>Correct Names: {correct_names} ({correct_names / identified_roms:.1%} of identified)</p>
    </div>
    
    <h2>Details</h2>
    <table>
        <tr>
            <th>File Name</th>
            <th>Identified</th>
            <th>Match Type</th>
            <th>Confidence</th>
            <th>Correct Name</th>
            <th>Name Matches</th>
        </tr>
    """
    
    for result in results:
        file_name = result.get('file_name', '')
        identified = result.get('identified', False)
        match_type = result.get('match_type', 'N/A')
        match_confidence = result.get('match_confidence', 0.0)
        correct_name = result.get('correct_name', 'N/A')
        name_matches = result.get('name_matches', False)
        
        status_class = 'success' if identified else 'error'
        name_class = 'success' if name_matches else ('warning' if identified else 'error')
        
        html += f"""
        <tr>
            <td>{file_name}</td>
            <td class="{status_class}">{identified}</td>
            <td>{match_type}</td>
            <td>{match_confidence:.1%}</td>
            <td>{correct_name}</td>
            <td class="{name_class}">{name_matches}</td>
        </tr>
        """
    
    html += """
    </table>
</body>
</html>
    """
    
    return html

def generate_csv_report(results: List[Dict[str, Any]]) -> str:
    """
    Generate a CSV report from identification results.
    
    Args:
        results: List of identification results
        
    Returns:
        CSV report as a string
    """
    csv = "File Name,Identified,Match Type,Confidence,Correct Name,Name Matches\n"
    
    for result in results:
        file_name = result.get('file_name', '')
        identified = result.get('identified', False)
        match_type = result.get('match_type', 'N/A')
        match_confidence = result.get('match_confidence', 0.0)
        correct_name = result.get('correct_name', 'N/A')
        name_matches = result.get('name_matches', False)
        
        # Escape commas in fields
        file_name = f'"{file_name}"'
        correct_name = f'"{correct_name}"'
        
        csv += f"{file_name},{identified},{match_type},{match_confidence:.1%},{correct_name},{name_matches}\n"
    
    return csv

if __name__ == '__main__':
    main()
