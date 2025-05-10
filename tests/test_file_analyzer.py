import pytest
import pathlib
import tempfile
import os

from src.file_analyzer import FileAnalyzer

@pytest.fixture
def file_analyzer():
    """Fixture to create a FileAnalyzer instance for testing."""
    return FileAnalyzer()

@pytest.fixture
def sample_text_file():
    """Create a temporary text file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        temp_file.write("This is a sample work document about a personal project in finance.")
        temp_file.flush()
        yield pathlib.Path(temp_file.name)
    
    # Clean up the temporary file
    os.unlink(temp_file.name)

def test_file_analyzer_initialization(file_analyzer):
    """Test that FileAnalyzer initializes correctly."""
    assert file_analyzer is not None
    assert hasattr(file_analyzer, 'nlp')
    assert hasattr(file_analyzer, 'classifier')
    assert hasattr(file_analyzer, 'purpose_categories')

def test_extract_metadata(file_analyzer, sample_text_file):
    """Test metadata extraction for a file."""
    metadata = file_analyzer.extract_metadata(sample_text_file)
    
    assert isinstance(metadata, dict)
    assert 'name' in metadata
    assert 'extension' in metadata
    assert 'size' in metadata
    assert 'created' in metadata
    assert 'modified' in metadata
    assert 'year' in metadata
    
    assert metadata['extension'] == '.txt'
    assert metadata['name'] == sample_text_file.name.split('/')[-1]

def test_classify_file_purpose(file_analyzer, sample_text_file):
    """Test file purpose classification."""
    with open(sample_text_file, 'r') as f:
        content = f.read()
    
    purposes = file_analyzer.classify_file_purpose(content)
    
    assert isinstance(purposes, list)
    assert len(purposes) > 0
    
    # Check that at least one purpose is in the predefined categories
    assert any(purpose in file_analyzer.purpose_categories for purpose in purposes)

def test_analyze_file(file_analyzer, sample_text_file):
    """Test comprehensive file analysis."""
    analysis_result = file_analyzer.analyze_file(sample_text_file)
    
    assert isinstance(analysis_result, dict)
    assert 'metadata' in analysis_result
    assert 'purposes' in analysis_result
    assert 'content_preview' in analysis_result
    
    # Check metadata
    assert isinstance(analysis_result['metadata'], dict)
    
    # Check purposes
    assert isinstance(analysis_result['purposes'], list)
    
    # Check content preview
    assert isinstance(analysis_result['content_preview'], str)
    assert len(analysis_result['content_preview']) <= 500

def test_file_analysis_error_handling(file_analyzer):
    """Test error handling for non-existent or unreadable files."""
    non_existent_path = pathlib.Path('/path/to/non/existent/file.txt')
    
    with pytest.raises(Exception):
        file_analyzer.analyze_file(non_existent_path)

def test_classification_multi_label(file_analyzer):
    """Test that classification supports multiple labels."""
    test_content = """
    This document covers work-related tasks for a personal finance project 
    that involves academic research and family budgeting.
    """
    
    purposes = file_analyzer.classify_file_purpose(test_content)
    
    # Expect multiple purposes to be detected
    assert len(purposes) > 1
    assert all(purpose in file_analyzer.purpose_categories for purpose in purposes)

# Optional: Performance and memory usage test
def test_file_analyzer_performance(file_analyzer, sample_text_file):
    """Basic performance test to ensure analysis doesn't take too long."""
    import time
    
    start_time = time.time()
    file_analyzer.analyze_file(sample_text_file)
    end_time = time.time()
    
    # Ensure analysis takes less than 1 second
    assert end_time - start_time < 1.0

if __name__ == '__main__':
    pytest.main([__file__])
