# Hardware Architecture Analyzer

A Python-based tool for analyzing hardware architecture simulator source code, extracting architectural patterns, control flow, data flow, and component relationships.

## Quick Start

### Installation

1. Install required packages:


### Basic Usage

To analyze a simulator project:

1. Make sure you have the following files in your working directory:
   - `analyze_project.py` (main entry point)
   - `arch_analyzer.py` (architecture pattern analyzer)
   - `go_analyzer.py` (Go code parser)

2. Run the analysis:


The analyzer will:
- Parse all Go files in the project
- Generate AST analysis
- Extract architectural patterns
- Create relationship maps
- Output analysis summary

## Output Files

The analyzer generates several files:

1. Component-level Analysis (`ast_analysis/`):
   - `core_analysis.json`: Core component structures
   - `cgra_analysis.json`: CGRA-specific components
   - `api_analysis.json`: API interfaces
   - `config_analysis.json`: Configuration structures
   - `samples_analysis.json`: Example implementations

2. Architecture Analysis (`architecture_analysis.json`):
   - Component relationships
   - Control flow patterns
   - Data flow patterns
   - Interface definitions

## Analysis Results

The analyzer provides:

1. Component Analysis:
   - Major architectural components
   - Component relationships
   - Interface definitions
   - Type hierarchies

2. Flow Analysis:
   - Control flow patterns (conditions, loops, etc.)
   - Data flow patterns (input/output, channels)
   - Communication paths

3. Metrics:
   - Component count
   - Relationship mappings
   - Pattern distributions
   - Interface complexity

## Using Analysis Results

### For LLM Processing

1. Start with `architecture_analysis.json`:
   - High-level project structure
   - Component relationships
   - Key patterns and metrics

2. Explore component details in `ast_analysis/*.json`:
   - Detailed type information
   - Method signatures
   - Implementation patterns

3. Use metrics for project overview:
   - Component distribution
   - Complexity measures
   - Pattern frequencies

### For Manual Review

1. Check console output for:
   - Key components list
   - Control flow patterns
   - Data flow distributions
   - Relationship summaries

2. Review generated JSON files:
   - Use a JSON viewer for better readability
   - Focus on relationships and patterns
   - Check interface definitions

## Tips for Best Results

1. Project Structure:
   - Use clear directory organization
   - Group related components
   - Maintain consistent naming

2. Analysis Process:
   - Ensure all dependencies are installed
   - Use absolute paths when possible
   - Review generated files systematically

3. Common Issues:
   - Missing tree-sitter packages: Install required language support
   - Parse errors: Check file permissions and encoding
   - Memory issues: Consider analyzing components separately

## Example Output Structure
