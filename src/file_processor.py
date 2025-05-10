import os
import json
import pathlib
from typing import List, Optional

from file_analyzer import FileAnalyzer

def process_files(directory: pathlib.Path, output_dir: Optional[pathlib.Path] = None) -> List[dict]:
    """
    Process files in a given directory using FileAnalyzer.

    Args:
        directory: Directory containing files to analyze
        output_dir: Optional directory to save analysis results

    Returns:
        List of file analysis results
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
