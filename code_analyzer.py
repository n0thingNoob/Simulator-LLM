import os
import json
from typing import Dict, List, Union, Optional, Any
from tree_sitter import Language, Parser, Tree, Node
from pathlib import Path
import subprocess
import logging

class TreeSitterAnalyzer:
    """
    A code analyzer using tree-sitter for parsing and analyzing source code across multiple files and directories.
    Provides easy-to-use APIs for code analysis and outputs AST in JSON format.
    """

    def __init__(self, languages: Dict[str, str] = None):
        """
        Initialize the TreeSitterAnalyzer with supported programming languages.
        
        Args:
            languages (Dict[str, str]): Dictionary mapping file extensions to language names
                                      e.g., {'.py': 'python', '.js': 'javascript'}
        """
        self.languages = languages or {
            '.py': 'python',
            '.js': 'javascript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'cpp',
            '.h': 'cpp',
            '.hpp': 'cpp',
            '.go': 'go'
        }
        
        self.parsers = {}
        self._setup_parsers()

    def _setup_parsers(self) -> None:
        """Set up tree-sitter parsers for all supported languages."""
        # Build tree-sitter languages if not already built
        if not os.path.exists('build/my-languages.so'):
            self._build_languages()

        # Load the language library
        library_path = os.path.join(os.getcwd(), 'build/my-languages.so')
        for ext, lang_name in self.languages.items():
            try:
                lang = Language(library_path, lang_name)
                parser = Parser()
                parser.set_language(lang)
                self.parsers[ext] = parser
            except Exception as e:
                logging.error(f"Failed to set up parser for {lang_name}: {str(e)}")

    def _build_languages(self) -> None:
        """Build tree-sitter language parsers."""
        os.makedirs('build', exist_ok=True)
        
        # Clone language repositories if they don't exist
        language_repos = {
            'python': 'https://github.com/tree-sitter/tree-sitter-python',
            'javascript': 'https://github.com/tree-sitter/tree-sitter-javascript',
            'java': 'https://github.com/tree-sitter/tree-sitter-java',
            'cpp': 'https://github.com/tree-sitter/tree-sitter-cpp',
            'go': 'https://github.com/tree-sitter/tree-sitter-go'
        }

        for lang, repo in language_repos.items():
            if not os.path.exists(f'tree-sitter-{lang}'):
                subprocess.run(['git', 'clone', repo])

        # Build the languages
        Language.build_library(
            'build/my-languages.so',
            [f'tree-sitter-{lang}' for lang in language_repos.keys()]
        )

    def _node_to_dict(self, node: Node) -> Dict[str, Any]:
        """
        Convert a tree-sitter Node to a dictionary representation.
        
        Args:
            node (Node): Tree-sitter AST node
            
        Returns:
            Dict[str, Any]: Dictionary representation of the node
        """
        result = {
            'type': node.type,
            'start_point': {'row': node.start_point[0], 'column': node.start_point[1]},
            'end_point': {'row': node.end_point[0], 'column': node.end_point[1]},
            'children': []
        }

        if len(node.children) == 0:
            result['text'] = node.text.decode('utf-8')
        else:
            for child in node.children:
                result['children'].append(self._node_to_dict(child))

        return result

    def _tree_to_json(self, tree: Tree) -> Dict[str, Any]:
        """
        Convert a tree-sitter Tree to JSON format.
        
        Args:
            tree (Tree): Tree-sitter AST
            
        Returns:
            Dict[str, Any]: JSON representation of the AST
        """
        return self._node_to_dict(tree.root_node)

    def parse_file(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """
        Parse a single file and return its AST in JSON format.
        
        Args:
            file_path (Union[str, Path]): Path to the source code file
            
        Returns:
            Optional[Dict[str, Any]]: JSON representation of the AST or None if parsing fails
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logging.error(f"File not found: {file_path}")
            return None

        ext = file_path.suffix
        if ext not in self.parsers:
            logging.error(f"Unsupported file extension: {ext}")
            return None

        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            tree = self.parsers[ext].parse(content)
            return {
                'file_path': str(file_path),
                'language': self.languages[ext],
                'ast': self._tree_to_json(tree)
            }
        except Exception as e:
            logging.error(f"Error parsing file {file_path}: {str(e)}")
            return None

    def parse_directory(self, 
                       directory_path: Union[str, Path], 
                       recursive: bool = True,
                       file_pattern: str = "*") -> List[Dict[str, Any]]:
        """
        Parse all supported files in a directory and return their ASTs.
        
        Args:
            directory_path (Union[str, Path]): Path to the directory
            recursive (bool): Whether to scan subdirectories recursively
            file_pattern (str): Pattern to match files (e.g., "*.py" for Python files only)
            
        Returns:
            List[Dict[str, Any]]: List of JSON representations of ASTs
        """
        directory_path = Path(directory_path)
        if not directory_path.exists():
            logging.error(f"Directory not found: {directory_path}")
            return []

        results = []
        pattern = "**/*" if recursive else "*"
        for file_path in directory_path.glob(pattern + file_pattern):
            if file_path.is_file() and file_path.suffix in self.parsers:
                ast = self.parse_file(file_path)
                if ast:
                    results.append(ast)

        return results

    def save_ast_to_json(self, 
                        ast_data: Union[Dict[str, Any], List[Dict[str, Any]]], 
                        output_path: Union[str, Path]) -> None:
        """
        Save AST data to a JSON file.
        
        Args:
            ast_data (Union[Dict[str, Any], List[Dict[str, Any]]]): AST data to save
            output_path (Union[str, Path]): Path to save the JSON file
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(ast_data, f, indent=2, ensure_ascii=False)
            logging.info(f"AST data saved to {output_path}")
        except Exception as e:
            logging.error(f"Error saving AST data: {str(e)}")

def main():
    """Example usage of the TreeSitterAnalyzer."""
    # Initialize the analyzer
    analyzer = TreeSitterAnalyzer()
    
    # Parse a single file
    ast = analyzer.parse_file("example.py")
    if ast:
        analyzer.save_ast_to_json(ast, "single_file_ast.json")
    
    # Parse a directory recursively
    asts = analyzer.parse_directory("project_directory")
    if asts:
        analyzer.save_ast_to_json(asts, "project_asts.json")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()