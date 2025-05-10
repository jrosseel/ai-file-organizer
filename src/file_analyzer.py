import os
import json
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
    """
    Initialize the FileAnalyzer with NLP models for content analysis.
    
    :param models_path: Optional path to pre-trained models
    :param categories_path: Optional path to categories JSON file
    """
    def __init__(self, models_path: str = None, categories_path: str = None):
       
        # Load classification categories
        self._load_classification_config(categories_path)
        
        # Initialize NLP and ML models
        self._initialize_nlp_models()

    """
    Load classification categories from a JSON configuration file.
    
    Attempts to load categories from the specified path or a default location.
    If loading fails, falls back to predefined default categories.
    
    :param categories_path: Optional path to the categories JSON file
    """
    def _load_classification_config(self, categories_path: Optional[str] = None) -> None:
        
        # Determine default categories path if not provided
        if categories_path is None:
            categories_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 'resources', 'categories.json'
            )
        
        try:
            # Attempt to load categories from JSON file
            with open(categories_path, 'r') as f:
                categories = json.load(f)
            
            # Extract categories with fallback to empty lists
            self.purpose_categories = categories.get('purpose_categories', [])
            self.project_categories = categories.get('project_categories', [])
            self.version_types = categories.get('version_types', ['unique', 'draft', 'revised', 'final'])
        
        except Exception as e:
            # Log error and use default categories if loading fails
            print(f"Error loading categories: {e}")
            self.purpose_categories = [
                "Work", "Leisure", "Personal Projects", "Private", 
                "Family", "Education", "Finance", "Health"
            ]
            self.project_categories = [
                "Work", "Personal", "Academic", "Freelance"
            ]
            self.version_types = ['unique', 'draft', 'revised', 'final']

    """
    Initialize Natural Language Processing and Machine Learning models.
    
    Sets up spaCy for text processing and Hugging Face for zero-shot classification.
    Handles model download if not already present.
    """
    def _initialize_nlp_models(self) -> None:

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
        
        # Initialize TF-IDF Vectorizer for content similarity
        self.vectorizer = TfidfVectorizer(stop_words='english')

    """
    Extract comprehensive metadata for a given file.
    
    Retrieves file attributes including name, extension, size, creation time,
    modification time, and creation year.
    
    :param file_path: Path to the file to extract metadata from
    :return: Dictionary containing file metadata
    :raises Exception: If file metadata cannot be accessed
    """
    def extract_metadata(self, file_path: pathlib.Path) -> Dict[str, Any]:  
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

    """
    Classify the purpose of a file using zero-shot classification.
    
    Uses a pre-trained zero-shot classification model to assign
    one or more purpose categories to the file content. Categories
    are determined by comparing the content against predefined purpose labels.
    
    :param file_content: Textual content of the file to classify
    :return: List of purpose categories with confidence above 0.5
    :raises Exception: If classification pipeline encounters an error
    """
    def classify_file_purpose(self, file_content: str) -> List[str]:
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

    """
    Perform comprehensive file analysis.
    
    :param file_path: Path to the file to analyze
    :return: Analysis results
    """
    def analyze_file(self, file_path: pathlib.Path) -> Dict[str, Any]:
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
