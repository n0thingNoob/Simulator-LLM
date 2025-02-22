from collections import defaultdict
from typing import Dict, List, Optional

class CodeAnalyzer:
    def __init__(self):
        self.symbol_table = defaultdict(list)
        self.dependency_graph = defaultdict(list)
        self.interface_map = {}

    def analyze_ast(self, ast: dict, file_path: str, lang: str):
        """Main analysis entry point"""
        if lang in ['c', 'cpp']:
            self._analyze_c_family(ast, file_path)
        elif lang == 'go':
            self._analyze_go(ast, file_path)

    def _analyze_c_family(self, node: dict, file_path: str):
        """Analyze C/C++ code structures"""
        if node['type'] == 'function_definition':
            self._process_c_function(node, file_path)
        elif node['type'] == 'struct_specifier':
            self._process_c_struct(node, file_path)
        elif node['type'] == 'declaration':
            self._process_c_declaration(node, file_path)
        
        # Recursively analyze child nodes
        for child in node.get('children', []):
            self._analyze_c_family(child, file_path)

    def _analyze_go(self, node: dict, file_path: str):
        """Analyze Go code structures"""
        if node['type'] == 'function_declaration':
            self._process_go_function(node, file_path)
        elif node['type'] == 'type_declaration':
            self._process_go_type(node, file_path)
        
        # Recursively analyze child nodes
        for child in node.get('children', []):
            self._analyze_go(child, file_path)

    def _process_c_function(self, node: dict, file_path: str):
        """Process C/C++ function definition"""
        func_name = self._get_c_function_name(node)
        return_type = self._get_c_return_type(node)
        parameters = self._get_c_parameters(node)
        
        self._add_symbol('functions', func_name, file_path, node)
        self._update_dependencies(func_name, parameters)

    def _process_c_struct(self, node: dict, file_path: str):
        """Process C/C++ struct definition"""
        struct_name = self._get_c_struct_name(node)
        fields = self._get_c_struct_fields(node)
        
        self._add_symbol('structs', struct_name, file_path, node)
        self.interface_map[struct_name] = fields

    def _process_go_function(self, node: dict, file_path: str):
        """Process Go function/method"""
        func_name = self._get_go_function_name(node)
        receiver = self._get_go_receiver(node)
        parameters = self._get_go_parameters(node)
        
        self._add_symbol('functions', func_name, file_path, node)
        if receiver:
            self.dependency_graph[receiver].append(func_name)

    def _process_go_type(self, node: dict, file_path: str):
        """Process Go type declarations"""
        if any(child['type'] == 'struct_type' for child in node['children']):
            struct_name = self._get_go_struct_name(node)
            methods = self._get_go_struct_methods(struct_name)
            self._add_symbol('structs', struct_name, file_path, node)
            self.interface_map[struct_name] = methods

    def _add_symbol(self, category: str, name: str, file_path: str, node: dict):
        """Add symbol to symbol table"""
        symbol_info = {
            'name': name,
            'file': file_path,
            'location': {
                'start_line': node['start']['line'],
                'end_line': node['end']['line'],
                'start_byte': node['start_byte'],
                'end_byte': node['end_byte']
            },
            'source_snippet': self._get_node_text(node)
        }
        self.symbol_table[category].append(symbol_info)

    def _update_dependencies(self, symbol: str, dependencies: List[str]):
        """Update dependency graph"""
        for dep in dependencies:
            if dep in self.interface_map:
                self.dependency_graph[symbol].append(dep)

    def _get_node_text(self, node: dict) -> str:
        """Extract source code text from AST node"""
        try:
            return node['source'][node['start_byte']:node['end_byte']].decode('utf8')
        except (KeyError, AttributeError):
            return ""

    def _get_c_function_name(self, node: dict) -> str:
        """Extract C/C++ function name"""
        declarator = self._find_child(node, 'declarator')
        return self._get_identifier(declarator) if declarator else "anonymous"

    def _get_c_return_type(self, node: dict) -> str:
        """Extract C/C++ function return type"""
        type_node = self._find_child(node, 'type_identifier')
        return self._get_node_text(type_node) if type_node else "void"

    def _get_c_parameters(self, node: dict) -> List[str]:
        """Extract C/C++ function parameters"""
        params = []
        param_list = self._find_child(node, 'parameter_list')
        if param_list:
            for param in param_list['children']:
                if param['type'] == 'parameter_declaration':
                    param_type = self._find_child(param, 'type_identifier')
                    param_name = self._find_child(param, 'identifier')
                    params.append(f"{self._get_node_text(param_type)} {self._get_node_text(param_name)}")
        return params

    def _get_c_struct_name(self, node: dict) -> str:
        """Extract C/C++ struct name"""
        name_node = self._find_child(node, 'name')
        return self._get_identifier(name_node) if name_node else "anonymous_struct"

    def _get_c_struct_fields(self, node: dict) -> Dict[str, str]:
        """Extract C/C++ struct fields"""
        fields = {}
        field_list = self._find_child(node, 'field_declaration_list')
        if field_list:
            for field in field_list['children']:
                if field['type'] == 'field_declaration':
                    field_type = self._find_child(field, 'type_identifier')
                    field_name = self._find_child(field, 'field_identifier')
                    fields[self._get_node_text(field_name)] = self._get_node_text(field_type)
        return fields

    def _get_go_function_name(self, node: dict) -> str:
        """Extract Go function name with receiver"""
        receiver = self._get_go_receiver(node)
        name_node = self._find_child(node, 'identifier') or self._find_child(node, 'field_identifier')
        base_name = self._get_identifier(name_node) if name_node else "anonymous"
        return f"{receiver}.{base_name}" if receiver else base_name

    def _get_go_receiver(self, node: dict) -> Optional[str]:
        """Extract Go method receiver"""
        receiver_list = self._find_child(node, 'parameter_list')
        if receiver_list and len(receiver_list['children']) > 0:
            return self._get_node_text(receiver_list['children'][0])
        return None

    def _get_go_parameters(self, node: dict) -> List[str]:
        """Extract Go function parameters"""
        params = []
        param_list = self._find_child(node, 'parameter_list')
        if param_list:
            for param in param_list['children']:
                if param['type'] == 'parameter_declaration':
                    param_name = self._find_child(param, 'identifier')
                    param_type = self._find_child(param, 'type_identifier')
                    params.append(f"{self._get_node_text(param_name)} {self._get_node_text(param_type)}")
        return params

    def _get_go_struct_name(self, node: dict) -> str:
        """Extract Go struct name"""
        type_spec = self._find_child(node, 'type_spec')
        name_node = self._find_child(type_spec, 'type_identifier') if type_spec else None
        return self._get_identifier(name_node) if name_node else "anonymous_go_struct"

    def _get_go_struct_methods(self, struct_name: str) -> List[str]:
        """Get methods associated with a Go struct"""
        return [func['name'] for func in self.symbol_table['functions'] 
                if func['name'].startswith(f"({struct_name})")]

    def _find_child(self, node: dict, target_type: str) -> Optional[dict]:
        """Recursively find child node by type"""
        if not node:
            return None
            
        for child in node.get('children', []):
            if child['type'] == target_type:
                return child
            found = self._find_child(child, target_type)
            if found:
                return found
        return None

    def _get_identifier(self, node: Optional[dict]) -> str:
        """Safely extract identifier from node"""
        return self._get_node_text(node) if node else ""

    def generate_report(self) -> dict:
        """Generate analysis report"""
        return {
            'symbols': dict(self.symbol_table),
            'dependencies': dict(self.dependency_graph),
            'interfaces': self.interface_map
        }