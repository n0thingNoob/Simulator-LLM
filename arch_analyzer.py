import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
import networkx as nx

class ArchitectureAnalyzer:
    """
    A general-purpose architecture simulator analyzer that extracts relationships,
    control flow, and data flow patterns from source code ASTs.
    """
    
    def __init__(self, analysis_dir: str):
        self.analysis_dir = analysis_dir
        # Patterns for identifying different architectural elements
        self.patterns = {
            'component': {
                'identifiers': [
                    'component', 'module', 'unit', 'block', 'element',
                    'processor', 'core', 'engine', 'accelerator'
                ],
                'types': [
                    'struct_type', 'interface_type', 'class_declaration',
                    'type_declaration'
                ]
            },
            'control_flow': {
                'identifiers': [
                    'control', 'schedule', 'dispatch', 'orchestrate',
                    'execute', 'step', 'cycle', 'tick', 'clock'
                ],
                'types': [
                    'function_declaration', 'method_declaration',
                    'if_statement', 'switch_statement', 'for_statement'
                ]
            },
            'data_flow': {
                'identifiers': [
                    'data', 'input', 'output', 'stream', 'flow', 'buffer',
                    'queue', 'channel', 'port', 'signal'
                ],
                'types': [
                    'field_declaration', 'variable_declaration',
                    'channel_type', 'array_type'
                ]
            },
            'state': {
                'identifiers': [
                    'state', 'status', 'mode', 'configuration', 'setting',
                    'parameter', 'register'
                ],
                'types': [
                    'field_declaration', 'variable_declaration',
                    'const_declaration'
                ]
            }
        }
        
        self.relationship_graph = nx.DiGraph()

    def _load_analysis_file(self, filename: str) -> Dict:
        """Load and parse a JSON analysis file."""
        filepath = os.path.join(self.analysis_dir, filename)
        with open(filepath, 'r') as f:
            return json.load(f)

    def _extract_name(self, node: Dict) -> Optional[str]:
        """Extract name from a node."""
        if 'text' in node:
            return node['text']
        for child in node.get('children', []):
            if child.get('type') in ['identifier', 'field_identifier']:
                return child.get('text')
        return None

    def _match_pattern(self, node: Dict, pattern_type: str) -> bool:
        """Check if node matches a specific pattern type."""
        node_type = node.get('type', '').lower()
        node_text = str(node.get('text', '')).lower()
        
        patterns = self.patterns[pattern_type]
        return (
            node_type in patterns['types'] or
            any(id_pattern in node_text for id_pattern in patterns['identifiers'])
        )

    def _extract_relationships(self, node: Dict, parent_info: Optional[Dict] = None) -> List[Dict]:
        """Extract relationships between architectural components."""
        relationships = []
        current_info = None
        
        # Check if current node represents a component
        if self._match_pattern(node, 'component'):
            current_info = {
                'name': self._extract_name(node),
                'type': node.get('type'),
                'location': {
                    'start': node.get('start_point'),
                    'end': node.get('end_point')
                }
            }
            
            # Add relationship with parent if exists
            if parent_info:
                relationships.append({
                    'from': parent_info['name'],
                    'to': current_info['name'],
                    'type': 'contains'
                })
        
        # Process children
        for child in node.get('children', []):
            child_rels = self._extract_relationships(child, current_info or parent_info)
            relationships.extend(child_rels)
            
        return relationships

    def _extract_control_flow(self, node: Dict) -> List[Dict]:
        """Extract control flow patterns."""
        patterns = []
        
        if self._match_pattern(node, 'control_flow'):
            pattern = {
                'type': 'control_flow',
                'name': self._extract_name(node),
                'node_type': node.get('type'),
                'location': {
                    'start': node.get('start_point'),
                    'end': node.get('end_point')
                },
                'children': []
            }
            patterns.append(pattern)
        
        for child in node.get('children', []):
            child_patterns = self._extract_control_flow(child)
            patterns.extend(child_patterns)
        
        return patterns

    def _extract_data_flow(self, node: Dict) -> List[Dict]:
        """Extract data flow patterns."""
        patterns = []
        
        if self._match_pattern(node, 'data_flow'):
            pattern = {
                'type': 'data_flow',
                'name': self._extract_name(node),
                'node_type': node.get('type'),
                'location': {
                    'start': node.get('start_point'),
                    'end': node.get('end_point')
                },
                'direction': self._determine_data_direction(node)
            }
            patterns.append(pattern)
        
        for child in node.get('children', []):
            child_patterns = self._extract_data_flow(child)
            patterns.extend(child_patterns)
        
        return patterns

    def _determine_data_direction(self, node: Dict) -> str:
        """Determine data flow direction based on node context."""
        text = str(node.get('text', '')).lower()
        if any(x in text for x in ['input', 'in', 'receive']):
            return 'in'
        elif any(x in text for x in ['output', 'out', 'send']):
            return 'out'
        return 'bidirectional'

    def analyze_file(self, ast_data: Dict) -> Dict[str, Any]:
        """Analyze patterns in a single file."""
        if 'ast' not in ast_data:
            return {}
            
        root_node = ast_data['ast']
        analysis = {
            'relationships': self._extract_relationships(root_node),
            'control_flow': self._extract_control_flow(root_node),
            'data_flow': self._extract_data_flow(root_node)
        }
        
        return analysis

    def build_relationship_graph(self, relationships: List[Dict]):
        """Build a directed graph of component relationships."""
        for rel in relationships:
            self.relationship_graph.add_edge(
                rel['from'],
                rel['to'],
                type=rel['type']
            )

    def analyze_architecture(self) -> Dict[str, Any]:
        """Perform comprehensive architecture analysis."""
        analysis_files = [f for f in os.listdir(self.analysis_dir)
                         if f.endswith('_analysis.json')]
        
        architecture_analysis = {
            'components': set(),
            'relationships': [],
            'control_flow_patterns': [],
            'data_flow_patterns': [],
            'metrics': {
                'total_components': 0,
                'total_relationships': 0,
                'control_flow_count': 0,
                'data_flow_count': 0
            }
        }
        
        # Analyze each file
        for analysis_file in analysis_files:
            data = self._load_analysis_file(analysis_file)
            for file_analysis in data.get('analysis', []):
                if 'ast' in file_analysis:
                    file_patterns = self.analyze_file(file_analysis['ast'])
                    
                    # Update relationships
                    architecture_analysis['relationships'].extend(file_patterns['relationships'])
                    
                    # Update control flow patterns
                    architecture_analysis['control_flow_patterns'].extend(file_patterns['control_flow'])
                    
                    # Update data flow patterns
                    architecture_analysis['data_flow_patterns'].extend(file_patterns['data_flow'])
                    
                    # Extract components
                    for rel in file_patterns['relationships']:
                        architecture_analysis['components'].add(rel['from'])
                        architecture_analysis['components'].add(rel['to'])
        
        # Build relationship graph
        self.build_relationship_graph(architecture_analysis['relationships'])
        
        # Calculate metrics
        architecture_analysis['metrics'].update({
            'total_components': len(architecture_analysis['components']),
            'total_relationships': len(architecture_analysis['relationships']),
            'control_flow_count': len(architecture_analysis['control_flow_patterns']),
            'data_flow_count': len(architecture_analysis['data_flow_patterns'])
        })
        
        # Convert sets to lists for JSON serialization
        architecture_analysis['components'] = list(architecture_analysis['components'])
        
        return architecture_analysis

    def save_analysis(self, output_file: str = 'architecture_analysis.json'):
        """Generate and save architecture analysis."""
        analysis = self.analyze_architecture()
        
        # Add metadata for LLM processing
        analysis['metadata'] = {
            'description': 'Architecture Simulator Analysis',
            'version': '1.0',
            'summary': {
                'components': len(analysis['components']),
                'relationships': len(analysis['relationships']),
                'control_flow_patterns': len(analysis['control_flow_patterns']),
                'data_flow_patterns': len(analysis['data_flow_patterns'])
            }
        }
        
        # Save analysis results
        output_path = os.path.join(self.analysis_dir, output_file)
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        return analysis

    def print_analysis_summary(self, analysis: Dict[str, Any]):
        """Print a human-readable summary of the analysis."""
        print("\nArchitecture Analysis Summary")
        print("=" * 50)
        print(f"Total Components: {analysis['metrics']['total_components']}")
        print(f"Total Relationships: {analysis['metrics']['total_relationships']}")
        print(f"Control Flow Patterns: {analysis['metrics']['control_flow_count']}")
        print(f"Data Flow Patterns: {analysis['metrics']['data_flow_count']}")
        
        print("\nKey Components:")
        for component in sorted(analysis['components'])[:10]:  # Show top 10
            print(f"- {component}")
            
        print("\nControl Flow Patterns:")
        control_patterns = defaultdict(int)
        for pattern in analysis['control_flow_patterns']:
            control_patterns[pattern['node_type']] += 1
        for pattern_type, count in sorted(control_patterns.items()):
            print(f"- {pattern_type}: {count}")
            
        print("\nData Flow Patterns:")
        data_patterns = defaultdict(int)
        for pattern in analysis['data_flow_patterns']:
            data_patterns[pattern['direction']] += 1
        for direction, count in sorted(data_patterns.items()):
            print(f"- {direction}: {count}")

def main():
    """Run architecture analysis."""
    analyzer = ArchitectureAnalyzer('.')
    analysis = analyzer.save_analysis()
    analyzer.print_analysis_summary(analysis)

if __name__ == "__main__":
    main()