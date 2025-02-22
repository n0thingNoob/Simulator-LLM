import os
import sys
import json
from pathlib import Path

# Add parent directory to path to import code_analyzer and arch_analyzer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from go_analyzer import GoAnalyzer
from arch_analyzer import ArchitectureAnalyzer

def analyze_go_files(project_path: str, output_dir: str):
    """Generate AST data for all Go files in the project."""
    analyzer = GoAnalyzer()
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all Go files
    go_files = []
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.go'):
                go_files.append(os.path.join(root, file))
    
    print(f"\nFound {len(go_files)} Go files to analyze")
    
    # Generate ASTs for each file
    component_asts = {}
    for file_path in go_files:
        rel_path = os.path.relpath(file_path, project_path)
        component = rel_path.split(os.sep)[0]  # Use top-level directory as component name
        
        if component not in component_asts:
            component_asts[component] = {
                'component': component,
                'analysis': []
            }
        
        print(f"Analyzing {rel_path}...")
        ast_data = analyzer.parse_file(file_path)
        if ast_data:
            component_asts[component]['analysis'].append({
                'file': rel_path,
                'ast': ast_data
            })
    
    # Save ASTs by component
    for component, data in component_asts.items():
        output_file = os.path.join(output_dir, f"{component}_analysis.json")
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved {component} analysis to {output_file}")
    
    return component_asts

def main():
    # Set up paths
    zeonica_path = os.path.join(os.getcwd(), 'zeonica')
    current_dir = os.getcwd()
    ast_output_dir = os.path.join(current_dir, 'ast_analysis')
    print(f"Current directory: {current_dir}")
    print(f"Zeonica path: {zeonica_path}")
    print(f"AST output directory: {ast_output_dir}")
    arch_output_dir = os.path.join(os.getcwd(), 'arch_analysis')
    
    # Create directories
    os.makedirs(ast_output_dir, exist_ok=True)
    os.makedirs(arch_output_dir, exist_ok=True)
    
    print("Starting Zeonica Project Analysis")
    print("=" * 50)
    
    # Step 1: Generate ASTs
    print("\nGenerating ASTs for Go files...")
    component_asts = analyze_go_files(zeonica_path, ast_output_dir)
    
    # Step 2: Run architecture analysis
    print("\nPerforming architecture analysis...")
    arch_analyzer = ArchitectureAnalyzer(ast_output_dir)
    analysis = arch_analyzer.save_analysis(os.path.join(arch_output_dir, 'architecture_analysis.json'))
    
    # Print analysis results
    arch_analyzer.print_analysis_summary(analysis)
    
    print("\nAnalysis files generated:")
    print(f"1. AST Analysis: {ast_output_dir}")
    print(f"2. Architecture Analysis: {arch_output_dir}")
    
    # Print LLM usage instructions
    print("\nFor LLM Usage:")
    print("-" * 50)
    print("1. AST analysis files contain raw syntax trees for each component")
    print("2. architecture_analysis.json contains:")
    print("   - Component relationships and dependencies")
    print("   - Control flow patterns")
    print("   - Data flow patterns")
    print("   - Interface definitions")
    print("3. Key metrics and patterns are in the metadata section")
    print("4. Use the components section to understand module structure")
    print("5. Relationship graphs show dependencies between components")

if __name__ == "__main__":
    main()