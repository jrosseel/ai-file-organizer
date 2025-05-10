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
def sample_files():
    """Create temporary files for similarity testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create similar files
        file1_path = pathlib.Path(temp_dir) / 'report.txt'
        file2_path = pathlib.Path(temp_dir) / 'report_draft.txt'
        file3_path = pathlib.Path(temp_dir) / 'completely_different.txt'
        
        # Write content to files
        file1_path.write_text("This is a sample work report about project management.")
        file2_path.write_text("This is a draft work report discussing project management strategies.")
        file3_path.write_text("Unrelated content about cooking and recipes.")
        
        yield file1_path, file2_path, file3_path

def test_calculate_file_similarity(file_analyzer, sample_files):
    """Test file similarity calculation."""
    file1, file2, file3 = sample_files
    
    # Compare similar files
    similarity_similar = file_analyzer.calculate_file_similarity(file1, file2)
    
    # Compare different files
    similarity_different = file_analyzer.calculate_file_similarity(file1, file3)
    
    # Assertions
    assert 'overall_similarity' in similarity_similar
    assert 'overall_similarity' in similarity_different
    
    # Similar files should have higher similarity
    assert similarity_similar['overall_similarity'] > similarity_different['overall_similarity']
    assert similarity_similar['overall_similarity'] > 0.5
    assert similarity_different['overall_similarity'] < 0.3

def test_generate_version_name(file_analyzer, sample_files):
    """Test version name generation."""
    file1, file2, _ = sample_files
    
    # Calculate similarity
    similarity = file_analyzer.calculate_file_similarity(file1, file2)
    
    # Generate version name
    version_name1 = file_analyzer.generate_version_name(file1, similarity)
    version_name2 = file_analyzer.generate_version_name(file2, similarity)
    
    # Assertions
    assert version_name1 != version_name2  # Should have unique identifiers
    assert version_name1.startswith('report')
    assert version_name1.endswith('.txt')
    assert 'v' in version_name1

def test_find_similar_files(file_analyzer, sample_files):
    """Test finding similar files in a directory."""
    file1, file2, file3 = sample_files
    temp_dir = file1.parent
    
    # Find similar files
    similar_files = file_analyzer.find_similar_files(temp_dir, similarity_threshold=0.5)
    
    # Assertions
    assert len(similar_files) > 0
    assert all(len(item) == 3 for item in similar_files)  # (file1, file2, similarity)
    
    # Check that similar files are detected
    similar_pairs = [(f1.name, f2.name) for f1, f2, _ in similar_files]
    assert ('report.txt', 'report_draft.txt') in similar_pairs or \
           ('report_draft.txt', 'report.txt') in similar_pairs

if __name__ == '__main__':
    pytest.main([__file__])
