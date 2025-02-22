# test_analyzer.py
import os
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from code_analyzer import TreeSitterAnalyzer

def print_json(data):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2))

def main():
    # Initialize analyzer
    analyzer = TreeSitterAnalyzer()
    
    # Create examples directory if it doesn't exist
    examples_dir = os.path.dirname(__file__)
    
    # Test Python file
    print("\nTesting Python file analysis...")
    python_ast = analyzer.parse_file(os.path.join(examples_dir, "example_python.py"))
    analyzer.save_ast_to_json(python_ast, os.path.join(examples_dir, "python_ast.json"))
    print("Python AST saved to python_ast.json")
    
    # Test C++ files
    print("\nTesting C++ file analysis...")
    cpp_ast = analyzer.parse_file(os.path.join(examples_dir, "example_cpp.cpp"))
    analyzer.save_ast_to_json(cpp_ast, os.path.join(examples_dir, "cpp_ast.json"))
    print("C++ AST saved to cpp_ast.json")
    
    header_ast = analyzer.parse_file(os.path.join(examples_dir, "example.h"))
    analyzer.save_ast_to_json(header_ast, os.path.join(examples_dir, "header_ast.json"))
    print("Header AST saved to header_ast.json")
    
    # Test Go file
    print("\nTesting Go file analysis...")
    go_ast = analyzer.parse_file(os.path.join(examples_dir, "example_go.go"))
    analyzer.save_ast_to_json(go_ast, os.path.join(examples_dir, "go_ast.json"))
    print("Go AST saved to go_ast.json")
    
    # Test directory parsing
    print("\nTesting directory parsing...")
    print("\nGathering ASTs from directory...")
    all_asts = []
    for ext in [".py", ".cpp", ".h", ".go"]:
        for file_path in [f for f in os.listdir(examples_dir) if f.endswith(ext)]:
            ast = analyzer.parse_file(os.path.join(examples_dir, file_path))
            if ast:
                all_asts.append(ast)
    
    analyzer.save_ast_to_json(all_asts, os.path.join(examples_dir, "all_asts.json"))
    print("All ASTs saved to all_asts.json")

if __name__ == "__main__":
    main()