import os
import sys
import json
from pathlib import Path
from code_analyzer import TreeSitterAnalyzer
from cgra_analyzer import CGRAAnalyzer

def analyze_component(analyzer, component_path, output_dir, component_name):
    """Analyze a specific component directory."""
    print(f"\nAnalyzing {component_name} component...")
    if os.path.exists(component_path):
        files = []
        for root, _, filenames in os.walk(component_path):
            for filename in filenames:
                if filename.endswith('.go'):
                    file_path = os.path.join(root, filename)
                    ast_data = analyzer.parse_file(file_path)
                    if ast_data:
                        files.append({
                            'file': os.path.relpath(file_path, component_path),
                            'ast': ast_data
                        })
        
        if files:
            output_file = os.path.join(output_dir, f"{component_name}_analysis.json")
            with open(output_file, 'w') as f:
                json.dump({
                    'component': component_name,
                    'files_analyzed': len(files),
                    'analysis': files
                }, f, indent=2)
            print(f"✓ {component_name.capitalize()} analysis completed: {len(files)} files analyzed")
            return len(files)
    return 0

def main():
    # Get zeonica project path
    zeonica_path = os.path.join(os.getcwd(), 'cgra_analysis', 'zeonica')
    if not os.path.exists(zeonica_path):
        print("Error: Zeonica project directory not found!")
        return

    # Create output directory
    output_dir = os.path.join(zeonica_path, 'analysis_results')
    os.makedirs(output_dir, exist_ok=True)

    # Initialize analyzer
    analyzer = CGRAAnalyzer()
    
    print("Starting CGRA analysis of zeonica project...")
    print("=" * 50)

    # Key components to analyze
    components = {
        'core': os.path.join(zeonica_path, 'core'),
        'cgra': os.path.join(zeonica_path, 'cgra'),
        'api': os.path.join(zeonica_path, 'api'),
        'config': os.path.join(zeonica_path, 'config'),
        'samples': os.path.join(zeonica_path, 'samples')
    }

    # Analyze each component
    total_files = 0
    analysis_summary = {
        'project_name': 'zeonica',
        'components': {},
        'total_files_analyzed': 0,
        'cgra_patterns': {
            'processing_elements': [],
            'interconnects': [],
            'memory_elements': [],
            'controllers': []
        }
    }

    for component_name, component_path in components.items():
        files_analyzed = analyze_component(analyzer, component_path, output_dir, component_name)
        total_files += files_analyzed
        analysis_summary['components'][component_name] = {
            'files_analyzed': files_analyzed,
            'path': os.path.relpath(component_path, zeonica_path)
        }

    analysis_summary['total_files_analyzed'] = total_files

    # Generate project-wide analysis
    project_analysis = analyzer.analyze_cgra_project(zeonica_path)
    with open(os.path.join(output_dir, 'project_analysis.json'), 'w') as f:
        json.dump(project_analysis, f, indent=2)

    # Save analysis summary
    with open(os.path.join(output_dir, 'analysis_summary.json'), 'w') as f:
        json.dump(analysis_summary, f, indent=2)

    print("\nAnalysis Summary:")
    print("=" * 50)
    print(f"Total files analyzed: {total_files}")
    print(f"Components processed: {', '.join(components.keys())}")
    print(f"\nAnalysis results saved to: {output_dir}")
    print("\nGenerated files:")
    for file in os.listdir(output_dir):
        print(f"- {file}")

    print("\nFor LLM Usage:")
    print("-" * 50)
    print("1. Start with analysis_summary.json for project overview")
    print("2. Explore individual component analyses for detailed structure")
    print("3. Reference project_analysis.json for CGRA-specific patterns")
    print("4. Key aspects to focus on:")
    print("   - Processing element definitions and relationships")
    print("   - Data flow patterns between components")
    print("   - Configuration and control mechanisms")
    print("   - Memory hierarchy and interconnect structure")

if __name__ == "__main__":
    main()