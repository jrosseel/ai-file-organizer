import os
import sys
import json
import pathlib
import argparse
from typing import List, Optional

# Add the current directory to Python path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from file_analyzer import FileAnalyzer

def process_files(directory: pathlib.Path, output_dir: Optional[pathlib.Path] = None) -> List[dict]:
    """
    Process files in a given directory using FileAnalyzer.
    
    :param directory: Directory containing files to analyze
    :param output_dir: Optional directory to save analysis results
    :return: List of file analysis results
    """
    # Initialize FileAnalyzer
    analyzer = FileAnalyzer()
    
    # Create output directory if specified
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Store analysis results
    analysis_results = []
    
    # Iterate through files in the directory
    for file_path in directory.rglob('*'):
        if file_path.is_file():
            try:
                # Analyze the file
                file_analysis = analyzer.analyze_file(file_path)
                analysis_results.append(file_analysis)
                
                # Optionally save results to output directory
                if output_dir:
                    result_filename = output_dir / f"{file_path.stem}_analysis.json"
                    with open(result_filename, 'w') as f:
                        json.dump(file_analysis, f, indent=4)
            
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
    
    return analysis_results

def main():
    """
    Main entry point for the file analysis CLI.
    
    Parses command-line arguments and initiates file processing.
    """
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
