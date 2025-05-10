import os
import pathlib
import difflib
import hashlib
from typing import List, Dict, Any, Optional, Tuple
import spacy
from transformers import pipeline
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class FileAnalyzer:
    def __init__(self, models_path: str = None):
        """
        Initialize the FileAnalyzer with NLP models for content analysis.
        
        :param models_path: Optional path to pre-trained models
        """
        # Initialize spaCy model for basic text processing
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            print("Downloading spaCy model...")
            spacy.cli.download('en_core_web_sm')
            self.nlp = spacy.load('en_core_web_sm')
        
        # Initialize Hugging Face zero-shot classification pipeline
        self.classifier = pipeline(
            "zero-shot-classification", 
            model="facebook/bart-large-mnli"
        )
        
        # Predefined classification categories
        self.purpose_categories = [
            "Work", "Leisure", "Personal Projects", "Private", 
            "Family", "Education", "Finance", "Health"
        ]
        
        self.project_categories = [
            "Work", "Personal", "Academic", "Freelance"
        ]

    def extract_metadata(self, file_path: pathlib.Path) -> Dict[str, Any]:
        """
        Extract file metadata for classification.
        
        :param file_path: Path to the file
        :return: Dictionary of file metadata
        """
        try:
            stats = file_path.stat()
            return {
                'name': file_path.name,
                'extension': file_path.suffix,
                'size': stats.st_size,
                'created': stats.st_ctime,
                'modified': stats.st_mtime,
                'year': pathlib.Path(file_path).stat().st_ctime_ns // (10**9) // 31536000 + 1970
            }
        except Exception as e:
            print(f"Error extracting metadata for {file_path}: {e}")
            return {}

    def classify_file_purpose(self, file_content: str) -> List[str]:
        """
        Classify file purpose using zero-shot classification.
        
        :param file_content: Text content of the file
        :return: List of purpose categories
        """
        try:
            # Perform zero-shot classification
            classification = self.classifier(
                file_content, 
                self.purpose_categories, 
                multi_label=True
            )
            
            # Filter categories above a confidence threshold
            return [
                category for category, score in 
                zip(classification['labels'], classification['scores']) 
                if score > 0.5
            ]
        except Exception as e:
            print(f"Classification error: {e}")
            return []

    def analyze_file(self, file_path: pathlib.Path) -> Dict[str, Any]:
        """
        Perform comprehensive file analysis.
        
        :param file_path: Path to the file to analyze
        :return: Analysis results
        """
        # Extract metadata
        metadata = self.extract_metadata(file_path)
        
        # Read file content (with size and type limitations)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Limit content reading to prevent memory issues
                content = f.read(100000)  # Read first 100KB
        except Exception as e:
            print(f"Could not read file {file_path}: {e}")
            content = ""
        
        # Classify purpose
        purposes = self.classify_file_purpose(content)
        
        return {
            'metadata': metadata,
            'purposes': purposes,
            'content_preview': content[:500]  # Preview first 500 chars
        }

def main():
    # Example usage
    analyzer = FileAnalyzer()
    test_file = pathlib.Path('/path/to/test/file.txt')
    result = analyzer.analyze_file(test_file)
    print(result)

if __name__ == '__main__':
    main()
