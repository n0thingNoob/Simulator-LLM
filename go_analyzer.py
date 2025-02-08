# go_analyzer.py
import os
from tree_sitter import Node

def analyze_go_file(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    tree = go_parser.parse(bytes(code, 'utf-8'))
    root = tree.root_node
    
    result = {
        'structs': [],
        'functions': [],
        'interfaces': []
    }
    
    def walk(node: Node):
        if node.type == 'type_spec':
            if node.child_by_field_name('type').type == 'struct_type':
                result['structs'].append(node.child_by_field_name('name').text.decode())
        elif node.type == 'function_declaration':
            result['functions'].append(node.child_by_field_name('name').text.decode())
        elif node.type == 'interface_type':
            result['interfaces'].append(node.parent.child_by_field_name('name').text.decode())
        
        for child in node.children:
            walk(child)
    
    walk(root)
    return result