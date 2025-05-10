import os
import json
import pathlib
from typing import List, Dict, Any, Optional
import spacy
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

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
    Advanced file purpose classification using multi-model approach.

    Utilizes multiple classification techniques to provide a comprehensive
    and nuanced file purpose classification:
    1. Zero-shot classification
    2. Semantic similarity
    3. Confidence-weighted scoring

    :param file_content: Textual content of the file to classify
    :param confidence_threshold: Minimum confidence score to include a category
    :return: Dictionary of purpose categories with their confidence scores
    :raises Exception: If classification pipeline encounters an error
    """
    def classify_file_purpose(self, file_content: str, confidence_threshold: float = 0.5) -> Dict[str, float]:
        try:
            # Perform zero-shot classification
            zero_shot_result = self.classifier(
                file_content, 
                self.purpose_categories, 
                multi_label=True
            )
            
            # Create initial classification dictionary
            classifications = dict(zip(
                zero_shot_result['labels'], 
                zero_shot_result['scores']
            ))
            
            # Enhance with semantic similarity
            doc = self.nlp(file_content)
            semantic_scores = {}
            for category in self.purpose_categories:
                category_doc = self.nlp(category)
                semantic_scores[category] = doc.similarity(category_doc)
            
            # Combine and weight scores
            final_scores = {}
            for category in self.purpose_categories:
                zero_shot_score = classifications.get(category, 0)
                semantic_score = semantic_scores.get(category, 0)
                
                # Weighted combination of scores
                final_score = (0.7 * zero_shot_score) + (0.3 * semantic_score)
                
                if final_score >= confidence_threshold:
                    final_scores[category] = final_score
            
            return final_scores
        
        except Exception as e:
            print(f"Advanced classification error: {e}")
            return {}

    """
    Perform comprehensive file analysis.
    
    Extracts file metadata, classifies purpose, and provides content preview.
    Uses advanced multi-model classification approach.
    
    :param file_path: Path to the file to analyze
    :return: Detailed file analysis results
    """
    def analyze_file(self, file_path: pathlib.Path) -> Dict[str, Any]:
        """
        Perform comprehensive file analysis.
        
        Extracts file metadata, classifies purpose, and provides content preview.
        Uses advanced multi-model classification approach.
        
        :param file_path: Path to the file to analyze
        :return: Detailed file analysis results
        """
        # Extract metadata
        metadata = self.extract_metadata(file_path)
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            content = ""
        
        # Classify file purpose with advanced multi-model approach
        purposes = self.classify_file_purpose(content)
        
        return {
            'path': str(file_path),
            'metadata': metadata,
            'purposes': purposes,
            'content_preview': content[:500],  # Preview first 500 chars
            'classification_method': 'advanced_multi_model'
        }
