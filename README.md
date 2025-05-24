# LLEMU - LLM-Enhanced ROM Management Utility

LLEMU is a ROM identification and management tool that uses checksum verification to accurately identify, verify, and rename ROM files according to standardized naming conventions.

## Current Features

- **Accurate ROM Identification**: Uses MD5, CRC32, and SHA1 checksums to precisely identify ROMs
- **Multiple Database Support**: Compatible with No-Intro, TOSEC, and other ROM databases
- **Standardized Renaming**: Renames ROMs according to established conventions
- **Dry Run Mode**: Preview changes before applying them
- **Detailed Reporting**: Generate comprehensive reports of verification results
- **Cross-Platform**: Works on macOS, Linux, and Windows

## LLM Integration Status

The "LLM-Enhanced" part of LLEMU's name reflects its design philosophy and future direction. Currently, LLEMU functions as a traditional ROM management utility using checksum-based verification without direct LLM integration.

### Future LLM Enhancements

In future versions, LLEMU aims to incorporate LLM capabilities for:
- Intelligent name correction for non-standard ROM names
- Classification of ROMs without database matches
- Enhanced metadata generation
- Natural language query processing
- Intelligent error resolution

Until these features are implemented, users can pair LLEMU with tools like Amazon Q or other AI assistants to enhance their ROM management workflow.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Required Python packages (see requirements.txt)
- ROM database files (DAT files) - not included, must be supplied by the user

### Installation
```bash
# Clone the repository
git clone https://github.com/oak2278/llemu.git

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage
```bash
# Scan ROMs without making changes (dry run)
python -m llemu scan --path /path/to/roms --dry-run

# Rename ROMs according to database
python -m llemu rename --path /path/to/roms

# Generate a verification report
python -m llemu report --path /path/to/roms --output report.html
```

## Database Files

LLEMU requires ROM database (DAT) files to function properly. These files are not included with LLEMU and must be supplied by the user. Place your DAT files in the `data/` directory or specify their location using command-line parameters.

## Project Structure
- `src/`: Core source code
- `data/`: ROM databases and cache (user-supplied)
- `logs/`: Log files
- `config/`: Configuration files
- `tests/`: Unit and integration tests

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
