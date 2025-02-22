from collections import defaultdict
from typing import Dict, List

class CodeAnalyzer:
    def __init__(self):
        self.symbol_table = defaultdict(list)
        
    def analyze_ast(self, ast: dict, file_path: str, lang: str):
        """Construct symbol table from AST"""
        if lang in ['c', 'cpp']:
            self._analyze_c_family(ast, file_path)
        elif lang == 'go':
            self._analyze_go(ast, file_path)
            
    def _analyze_c_family(self, node: dict, file_path: str):
        if node['type'] == 'function_definition':
            name = self._get_function_name(node)
            self.symbol_table['functions'].append({
                'name': name,
                'file': file_path,
                'lines': (node['start']['line'], node['end']['line'])
            })
            
        elif node['type'] == 'struct_specifier':
            name = self._get_struct_name(node)
            self.symbol_table['structs'].append({
                'name': name,
                'file': file_path
            })
            
    def _analyze_go(self, node: dict, file_path: str):
        if node['type'] == 'function_declaration':
            name = self._get_go_function_name(node)
            self.symbol_table['functions'].append({
                'name': name,
                'file': file_path,
                'type': 'go_func'
            })
            
        elif node['type'] == 'type_declaration':
            if any(child['type'] == 'struct_type' for child in node['children']):
                name = self._get_go_struct_name(node)
                self.symbol_table['structs'].append({
                    'name': name,
                    'file': file_path
                })
                
    def generate_report(self) -> dict:
        return {
            'functions': len(self.symbol_table['functions']),
            'structs': len(self.symbol_table['structs']),
            'details': dict(self.symbol_table)
        }
    
    def _get_function_name(self, node: dict) -> str:
        """Extract C/C++ function name"""
        # iterate declarator -> identifier
        for child in node['children']:
            if child['type'] == 'declarator':
                return self._find_identifier(child)
        return "anonymous"

    def _get_struct_name(self, node: dict) -> str:
        """Extract C/C++ struct name"""
        for child in node['children']:
            if child['type'] == 'name':
                return self._get_node_text(child)
        return "anonymous_struct"

    def _get_go_function_name(self, node: dict) -> str:
        """Extract Go function name"""
        # func (r *Receiver) Method()
        receiver = ""
        for child in node['children']:
            if child['type'] == 'method_spec':
                # Receiver
                receiver_node = self._find_child(child, 'parameter_list')
                if receiver_node:
                    receiver = self._get_node_text(receiver_node)
                # method name
                name_node = self._find_child(child, 'field_identifier')
                return f"{receiver}.{self._get_node_text(name_node)}"
            
            if child['type'] == 'identifier':
                return self._get_node_text(child)
        return "anonymous_go_func"

    def _get_go_struct_name(self, node: dict) -> str:
        """Extract Go struct name"""
        for child in node['children']:
            if child['type'] == 'type_spec':
                name_node = self._find_child(child, 'type_identifier')
                if name_node:
                    return self._get_node_text(name_node)
        return "anonymous_go_struct"

    def _find_child(self, node: dict, target_type: str) -> dict or None:
        """recursively find child node by type"""
        for child in node['children']:
            if child['type'] == target_type:
                return child
            found = self._find_child(child, target_type)
            if found:
                return found
        return None

    def _find_identifier(self, node: dict) -> str:
        """recursively find identifier node"""
        if node['type'] == 'identifier':
            return self._get_node_text(node)
        for child in node['children']:
            result = self._find_identifier(child)
            if result:
                return result
        return "unknown"

    def _get_node_text(self, node: dict) -> str:
        """Extract text from node"""
        # 注意：需要根据实际代码字符串计算位置
        # 这里简化实现，返回节点类型中的标识符
        if 'children' in node and node['children']:
            return node['children'][0]['type']
        return node['type'].split('_')[-1]