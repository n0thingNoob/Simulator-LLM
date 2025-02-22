import os
import json
from typing import Dict, List, Any, Optional, Set
import sys
from pathlib import Path

# Import base analyzer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from code_analyzer import TreeSitterAnalyzer

class CGRAAnalyzer(TreeSitterAnalyzer):
    """
    CGRA-specific code analyzer that extends TreeSitterAnalyzer with capabilities
    to understand CGRA architectural patterns and relationships.
    """
    
    def __init__(self):
        super().__init__()
        # CGRA-specific component patterns
        self.cgra_patterns = {
            'processing_elements': [
                'ProcessingElement',
                'PE',
                'ALU',
                'FunctionalUnit'
            ],
            'interconnects': [
                'Network',
                'Interconnect',
                'Router',
                'Switch'
            ],
            'memories': [
                'Memory',
                'Buffer',
                'Cache',
                'Register'
            ],
            'controls': [
                'Controller',
                'Scheduler',
                'Mapper'
            ],
            'configurations': [
                'Config',
                'Configuration',
                'Setting'
            ]
        }

    def _identify_component_type(self, node_dict: Dict) -> Optional[str]:
        """Identify CGRA component type from node name and structure."""
        if 'text' not in node_dict:
            return None
            
        text = node_dict['text'].lower()
        for comp_type, patterns in self.cgra_patterns.items():
            if any(pattern.lower() in text for pattern in patterns):
                return comp_type
        return None

    def _extract_interface_info(self, node_dict: Dict) -> Dict[str, Any]:
        """Extract interface information from struct/interface definitions."""
        interface_info = {
            'inputs': [],
            'outputs': [],
            'parameters': [],
            'methods': []
        }

        if node_dict['type'] in ['struct_type', 'interface_type']:
            for child in node_dict.get('children', []):
                if child['type'] == 'field_declaration':
                    field_info = self._extract_field_info(child)
                    interface_info['parameters'].append(field_info)
                elif child['type'] == 'method_declaration':
                    method_info = self._extract_method_info(child)
                    interface_info['methods'].append(method_info)

        return interface_info

    def _extract_field_info(self, node_dict: Dict) -> Dict[str, Any]:
        """Extract information from field declarations."""
        field_info = {
            'name': '',
            'type': '',
            'tags': []
        }

        for child in node_dict.get('children', []):
            if child['type'] == 'field_identifier':
                field_info['name'] = child.get('text', '')
            elif child['type'] == 'type_identifier':
                field_info['type'] = child.get('text', '')
            elif child['type'] == 'tag':
                field_info['tags'].append(child.get('text', ''))

        return field_info

    def _extract_method_info(self, node_dict: Dict) -> Dict[str, Any]:
        """Extract information from method declarations."""
        method_info = {
            'name': '',
            'parameters': [],
            'return_type': '',
            'receiver': None
        }

        for child in node_dict.get('children', []):
            if child['type'] == 'field_identifier':
                method_info['name'] = child.get('text', '')
            elif child['type'] == 'parameter_list':
                method_info['parameters'] = self._extract_parameters(child)
            elif child['type'] == 'receiver':
                method_info['receiver'] = self._extract_receiver(child)

        return method_info

    def _extract_parameters(self, node_dict: Dict) -> List[Dict[str, str]]:
        """Extract parameter information from parameter lists."""
        parameters = []
        for child in node_dict.get('children', []):
            if child['type'] == 'parameter_declaration':
                param = {
                    'name': '',
                    'type': ''
                }
                for param_child in child.get('children', []):
                    if param_child['type'] == 'identifier':
                        param['name'] = param_child.get('text', '')
                    elif param_child['type'] == 'type_identifier':
                        param['type'] = param_child.get('text', '')
                parameters.append(param)
        return parameters

    def _extract_receiver(self, node_dict: Dict) -> Dict[str, str]:
        """Extract receiver information from method declarations."""
        receiver = {
            'name': '',
            'type': ''
        }
        for child in node_dict.get('children', []):
            if child['type'] == 'identifier':
                receiver['name'] = child.get('text', '')
            elif child['type'] == 'type_identifier':
                receiver['type'] = child.get('text', '')
        return receiver

    def analyze_cgra_components(self, ast_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze CGRA components from AST data.
        
        Args:
            ast_data: AST data from parse_file or parse_directory
            
        Returns:
            Dict containing analyzed CGRA components and their relationships
        """
        components = {
            'processing_elements': [],
            'interconnects': [],
            'memories': [],
            'controls': [],
            'configurations': [],
            'relationships': []
        }

        def traverse_node(node: Dict, parent_type: Optional[str] = None):
            component_type = self._identify_component_type(node)
            
            if component_type:
                component_info = {
                    'type': component_type,
                    'name': node.get('text', ''),
                    'location': {
                        'start': node.get('start_point', {}),
                        'end': node.get('end_point', {})
                    },
                    'interface': self._extract_interface_info(node)
                }
                
                if parent_type:
                    components['relationships'].append({
                        'from': parent_type,
                        'to': component_type,
                        'type': 'contains'
                    })
                
                # Use the component type directly as key since it's already pluralized
                components[component_type].append(component_info)
            
            for child in node.get('children', []):
                traverse_node(child, component_type or parent_type)

        traverse_node(ast_data['ast'])
        return components

    def analyze_dataflow(self, ast_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze data flow patterns in CGRA design.
        
        Args:
            ast_data: AST data from parse_file or parse_directory
            
        Returns:
            Dict containing data flow analysis results
        """
        dataflow = {
            'channels': [],
            'connections': [],
            'patterns': []
        }
        
        def find_dataflow_patterns(node: Dict):
            if node['type'] in ['send_statement', 'receive_statement']:
                channel_info = {
                    'type': node['type'],
                    'location': {
                        'start': node.get('start_point', {}),
                        'end': node.get('end_point', {})
                    }
                }
                dataflow['channels'].append(channel_info)
            
            for child in node.get('children', []):
                find_dataflow_patterns(child)
        
        find_dataflow_patterns(ast_data['ast'])
        return dataflow

    def analyze_cgra_project(self, project_path: str) -> Dict[str, Any]:
        """
        Analyze entire CGRA project and generate comprehensive analysis.
        
        Args:
            project_path: Path to CGRA project root directory
            
        Returns:
            Dict containing complete project analysis
        """
        project_analysis = {
            'components': {},
            'dataflow': {},
            'configurations': {},
            'project_structure': {
                'core_components': [],
                'utilities': [],
                'tests': [],
                'samples': []
            }
        }
        
        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith('.go'):
                    file_path = os.path.join(root, file)
                    ast_data = self.parse_file(file_path)
                    
                    if ast_data:
                        relative_path = os.path.relpath(file_path, project_path)
                        components = self.analyze_cgra_components(ast_data)
                        dataflow = self.analyze_dataflow(ast_data)
                        
                        # Categorize file based on path
                        if 'test' in file:
                            project_analysis['project_structure']['tests'].append(relative_path)
                        elif 'samples' in relative_path:
                            project_analysis['project_structure']['samples'].append(relative_path)
                        elif any(key in relative_path.lower() for key in ['core', 'cgra', 'pe']):
                            project_analysis['project_structure']['core_components'].append(relative_path)
                        else:
                            project_analysis['project_structure']['utilities'].append(relative_path)
                        
                        # Merge component and dataflow analysis
                        for comp_type in components:
                            if comp_type not in project_analysis['components']:
                                project_analysis['components'][comp_type] = []
                            project_analysis['components'][comp_type].extend(components[comp_type])
                        
                        for flow_type in dataflow:
                            if flow_type not in project_analysis['dataflow']:
                                project_analysis['dataflow'][flow_type] = []
                            project_analysis['dataflow'][flow_type].extend(dataflow[flow_type])
        
        return project_analysis

    def save_cgra_analysis(self, analysis: Dict[str, Any], output_path: str):
        """
        Save CGRA analysis results in a structured format suitable for LLM processing.
        
        Args:
            analysis: Analysis results from analyze_cgra_project
            output_path: Path to save the analysis results
        """
        # Add LLM-friendly metadata
        analysis['metadata'] = {
            'description': 'CGRA Architecture Analysis',
            'version': '1.0',
            'analysis_type': 'cgra',
            'component_summary': {
                'total_components': sum(len(comps) for comps in analysis['components'].values()),
                'component_types': list(analysis['components'].keys()),
                'dataflow_patterns': len(analysis['dataflow'].get('patterns', [])),
                'files_analyzed': len(analysis['project_structure']['core_components']) +
                                len(analysis['project_structure']['utilities']) +
                                len(analysis['project_structure']['samples'])
            }
        }
        
        # Save to JSON with proper formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)