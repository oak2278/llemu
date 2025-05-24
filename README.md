# LLEMU - LLM-Enhanced ROM Management Utility

LLEMU is a modern ROM identification and management tool that uses advanced checksum verification and machine learning techniques to accurately identify, verify, and rename ROM files according to standardized naming conventions.

## Features

- **Accurate ROM Identification**: Uses MD5, CRC32, and SHA1 checksums to precisely identify ROMs
- **Multiple Database Support**: Compatible with No-Intro, TOSEC, and other ROM databases
- **Intelligent Renaming**: Standardizes ROM names according to established conventions
- **Dry Run Mode**: Preview changes before applying them
- **Detailed Reporting**: Generate comprehensive reports of verification results
- **Cross-Platform**: Works on macOS, Linux, and Windows

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Required Python packages (see requirements.txt)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/llemu.git

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

## Project Structure
- `src/`: Core source code
- `data/`: ROM databases and cache
- `logs/`: Log files
- `config/`: Configuration files
- `tests/`: Unit and integration tests

## License
MIT License

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
