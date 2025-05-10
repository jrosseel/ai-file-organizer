import os
import sys
import pathlib
import argparse

# Add the current directory to Python path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from file_processor import process_files

"""
Main entry point for the file analysis CLI.

Parses command-line arguments and initiates file processing.
"""
def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Advanced File Analyzer')
    parser.add_argument(
        'directory', 
        type=pathlib.Path, 
        help='Directory to analyze files in'
    )
    parser.add_argument(
        '-o', '--output', 
        type=pathlib.Path, 
        help='Optional output directory for analysis results'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate input directory
    if not args.directory.is_dir():
        print(f"Error: {args.directory} is not a valid directory.")
        sys.exit(1)
    
    # Process files
    results = process_files(args.directory, args.output)
    
    # Print summary
    print(f"Analyzed {len(results)} files.")

if __name__ == '__main__':
    main()
