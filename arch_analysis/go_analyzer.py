import os
import json
import subprocess
from typing import Dict, List, Any, Optional
from tree_sitter import Language, Parser, Tree, Node
from pathlib import Path

class GoAnalyzer:
    """A simplified analyzer focusing on Go language source code analysis."""
    
    def __init__(self):
        """Initialize the Go analyzer with Go language support."""
        self.parser = None
        self._setup_parser()

    def _setup_parser(self) -> None:
        """Set up tree-sitter parser for Go language."""
        if not os.path.exists('build/my-languages.so'):
            self._build_language()

        library_path = os.path.join(os.getcwd(), 'build/my-languages.so')
        lang = Language(library_path, 'go')
        self.parser = Parser()
        self.parser.set_language(lang)

    def _build_language(self) -> None:
        """Build tree-sitter Go language parser."""
        os.makedirs('build', exist_ok=True)
        
        # Clone Go language repository if it doesn't exist
        if not os.path.exists('tree-sitter-go'):
            subprocess.run(['git', 'clone', 'https://github.com/tree-sitter/tree-sitter-go'])

        # Build the language
        Language.build_library(
            'build/my-languages.so',
            ['tree-sitter-go']
        )

    def _node_to_dict(self, node: Node) -> Dict[str, Any]:
        """Convert a tree-sitter Node to a dictionary representation."""
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

    def parse_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse a Go source file and return its AST in JSON format."""
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return None

        if not file_path.suffix == '.go':
            print(f"Not a Go file: {file_path}")
            return None

        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            tree = self.parser.parse(content)
            return {
                'file_path': str(file_path),
                'language': 'go',
                'ast': self._node_to_dict(tree.root_node)
            }
        except Exception as e:
            print(f"Error parsing file {file_path}: {str(e)}")
            return None

    def extract_types(self, ast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract type declarations from AST."""
        types = []
        
        def traverse(node: Dict[str, Any]):
            if node['type'] in ['type_declaration', 'struct_type', 'interface_type']:
                types.append({
                    'type': node['type'],
                    'location': {
                        'start': node['start_point'],
                        'end': node['end_point']
                    },
                    'details': node
                })
            for child in node.get('children', []):
                traverse(child)
        
        traverse(ast['ast'])
        return types

    def extract_functions(self, ast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract function declarations from AST."""
        functions = []
        
        def traverse(node: Dict[str, Any]):
            if node['type'] == 'function_declaration':
                functions.append({
                    'type': 'function',
                    'location': {
                        'start': node['start_point'],
                        'end': node['end_point']
                    },
                    'details': node
                })
            for child in node.get('children', []):
                traverse(child)
        
        traverse(ast['ast'])
        return functions

    def extract_interfaces(self, ast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract interface declarations from AST."""
        interfaces = []
        
        def traverse(node: Dict[str, Any]):
            if node['type'] == 'interface_type':
                interfaces.append({
                    'type': 'interface',
                    'location': {
                        'start': node['start_point'],
                        'end': node['end_point']
                    },
                    'details': node
                })
            for child in node.get('children', []):
                traverse(child)
        
        traverse(ast['ast'])
        return interfaces

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Perform comprehensive analysis of a Go file."""
        ast_data = self.parse_file(file_path)
        if not ast_data:
            return {}
        
        analysis = {
            'file_path': ast_data['file_path'],
            'types': self.extract_types(ast_data),
            'functions': self.extract_functions(ast_data),
            'interfaces': self.extract_interfaces(ast_data)
        }
        
        return analysis

    def save_analysis(self, analysis: Dict[str, Any], output_path: str) -> None:
        """Save analysis results to JSON file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving analysis: {str(e)}")