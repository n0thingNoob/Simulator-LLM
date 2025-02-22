2. Generated Output:
- `ast_analysis/*.json`: Component-level AST analysis
- `architecture_analysis.json`: High-level architectural patterns
- Console summary of key metrics and patterns

## Key Features

1. Component Analysis
- Identification of major architectural components
- Interface and dependency mapping
- Component hierarchy extraction

2. Flow Analysis
- Control flow pattern detection
- Data flow path analysis
- Communication pattern identification

3. Pattern Recognition
- Common architectural patterns
- Hardware-specific constructs
- Interface definitions

## Tips for Using the Analyzer

1. Project Structure
- Ensure your simulator project uses clear directory structure
- Keep related components in dedicated directories
- Use consistent naming conventions

2. Analysis Results
- Check ast_analysis/ for detailed component structure
- Review architecture_analysis.json for high-level patterns
- Use the summary metrics for quick understanding

3. Common Issues
- Missing language parsers: Install required tree-sitter packages
- Parse errors: Check file permissions and encoding
- Memory issues: Consider analyzing subset of components

## Example Analysis Output
