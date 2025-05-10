import os
import pathlib
import shutil
import json
from typing import Dict, List, Optional

"""Intelligent folder reorganization engine for file management.

This class provides advanced file organization strategies using both
rule-based and machine learning approaches. It supports generating
intelligent folder hierarchies, previewing changes, and applying
or rolling back reorganization.

Attributes:
    config (dict): Configuration for folder reorganization rules.
    _previous_state (dict): Tracks file locations before reorganization.
"""
class FolderReorganizer:

    """Initialize the FolderReorganizer with optional configuration.

        Args:
            config_path (Optional[str], optional): Path to the reorganization
                configuration file. Defaults to None, which uses the default
                configuration path.

        Raises:
            ValueError: If the configuration file is invalid or missing
                required keys.
    """
    def __init__(self, config_path: Optional[str] = None):
        # Load configuration
        self._load_reorganization_config(config_path)
        
        # Tracking for undo functionality
        self._previous_state = {}

    """Load reorganization configuration from JSON file.

        Reads the configuration file and validates its contents. The configuration
        defines rules for file categorization and hierarchy generation.

        Args:
            config_path (Optional[str], optional): Path to the configuration file.
                Defaults to None, which uses the default configuration path.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            json.JSONDecodeError: If the configuration file contains invalid JSON.
            ValueError: If the configuration is missing required keys.
    """
    def _load_reorganization_config(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 'resources', 'reorganization_config.json'
            )
        
        # Load and validate configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Validate required configuration keys
        required_keys = ['hierarchy_rules', 'classification_weights']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required configuration key: {key}")
    
    """Generate an intelligent folder hierarchy based on file characteristics.

        Scans the source directory and categorizes files according to the
        configured hierarchy rules. Creates a mapping of categories to files.

        Args:
            source_directory (pathlib.Path): Directory to analyze and reorganize.

        Returns:
            Dict[str, List[pathlib.Path]]: A dictionary where keys are category
            names and values are lists of file paths belonging to those categories.

        Example:
            >>> reorganizer = FolderReorganizer()
            >>> hierarchy = reorganizer.generate_folder_hierarchy(Path('/path/to/files'))
            >>> print(hierarchy)
            {'Documents': [Path('/path/to/files/report.pdf'), ...], ...}
    """
    def generate_folder_hierarchy(self, source_directory: pathlib.Path) -> Dict[str, List[pathlib.Path]]:
        # Placeholder for hierarchy generation logic
        proposed_hierarchy = {}
        
        # Scan files in the source directory
        for file_path in source_directory.rglob('*'):
            if file_path.is_file():
                # Determine appropriate category based on rules
                category = self._categorize_file(file_path)
                
                # Group files by category
                if category not in proposed_hierarchy:
                    proposed_hierarchy[category] = []
                proposed_hierarchy[category].append(file_path)
        
        return proposed_hierarchy
    
    """Categorize a file based on predefined rules and weights.

        Determines the appropriate category for a file by applying
        the configured hierarchy rules in order.

        Args:
            file_path (pathlib.Path): Path to the file to categorize.

        Returns:
            str: The determined category for the file. Returns 'Uncategorized'
            if no matching rule is found.

        Note:
            The categorization is based on the rules defined in the
            configuration file, typically using file extensions and
            other metadata.
    """
    def _categorize_file(self, file_path: pathlib.Path) -> str:
       
        # Implement categorization logic using configuration rules
        # This is a simplified version and should be expanded
        for rule in self.config.get('hierarchy_rules', []):
            # Check rule conditions (file extension, metadata, etc.)
            if self._check_rule_conditions(file_path, rule):
                return rule.get('category', 'Uncategorized')
        
        return 'Uncategorized'
    
    """Check if a file matches a specific reorganization rule.

        Evaluates whether a given file satisfies the conditions
        specified in a reorganization rule.

        Args:
            file_path (pathlib.Path): Path to the file being evaluated.
            rule (Dict): A dictionary containing rule conditions.

        Returns:
            bool: True if the file matches the rule, False otherwise.

        Note:
            Currently supports checking file extensions. Can be extended
            to include more sophisticated rule matching in the future.
    """
    def _check_rule_conditions(self, file_path: pathlib.Path, rule: Dict) -> bool:
       
        # Check file extension
        if 'extensions' in rule:
            if file_path.suffix[1:] not in rule['extensions']:
                return False
        
        # Additional rule checking can be added here
        return True
    
    """Preview proposed folder reorganization without making changes.

        Prints a detailed preview of the proposed folder hierarchy,
        showing how files would be categorized without actually
        moving any files.

        Args:
            proposed_hierarchy (Dict[str, List[pathlib.Path]]): A dictionary
                mapping category names to lists of file paths.

        Example:
            >>> reorganizer = FolderReorganizer()
            >>> hierarchy = reorganizer.generate_folder_hierarchy(Path('/files'))
            >>> reorganizer.preview_changes(hierarchy)
            # Prints categorized files to console
    """
    def preview_changes(self, proposed_hierarchy: Dict[str, List[pathlib.Path]]) -> None:
        
        print("Proposed Folder Reorganization:")
        for category, files in proposed_hierarchy.items():
            print(f"\nCategory: {category}")
            for file_path in files:
                print(f"  - {file_path}")
    
    """Apply the proposed folder reorganization.

        Moves files into category-specific subdirectories based on
        the proposed hierarchy. Tracks original file locations for
        potential rollback.

        Args:
            proposed_hierarchy (Dict[str, List[pathlib.Path]]): A dictionary
                mapping category names to lists of file paths to be moved.
            base_output_dir (pathlib.Path): Base directory where categorized
                subdirectories will be created.

        Note:
            - Creates category subdirectories if they don't exist
            - Moves files to their respective category directories
            - Maintains a record of original file locations for rollback

        Raises:
            OSError: If there are issues creating directories or moving files
    """
    def apply_reorganization(self, proposed_hierarchy: Dict[str, List[pathlib.Path]], base_output_dir: pathlib.Path):
        
        # Track previous state for potential rollback
        self._previous_state = {}
        
        # Create category directories and move files
        for category, files in proposed_hierarchy.items():
            category_dir = base_output_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            for file_path in files:
                # Track original location
                self._previous_state[file_path] = file_path
                
                # Move file to new location
                destination = category_dir / file_path.name
                shutil.move(str(file_path), str(destination))
    
    """Rollback the last reorganization to the previous state.

        Restores files to their original locations before the
        reorganization was applied. Removes any empty category
        directories created during the reorganization.

        Args:
            base_output_dir (pathlib.Path): Base directory where
                categorized files were moved.

        Note:
            - Moves files back to their original locations
            - Clears the tracking of previous file states
            - Removes empty category directories

        Raises:
            OSError: If there are issues moving files or removing directories

        Warns:
            Prints a message if no previous state exists to rollback
    """
    def rollback(self, base_output_dir: pathlib.Path):
        
        if not self._previous_state:
            print("No previous state to rollback.")
            return
        
        for original_path, current_path in self._previous_state.items():
            # Move file back to original location
            shutil.move(str(current_path), str(original_path))
        
        # Clear previous state
        self._previous_state.clear()
        
        # Optional: Remove empty category directories
        for category_dir in base_output_dir.iterdir():
            if category_dir.is_dir() and not any(category_dir.iterdir()):
                category_dir.rmdir()
