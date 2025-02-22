from tree_sitter import Parser, Language
import os

class CodeParser:
    def __init__(self):
        self._build_languages()
        self.parsers = {
            'c': self._init_parser('c'),
            'cpp': self._init_parser('cpp'),
            'go': self._init_parser('go')
        }
        
    def _build_languages(self):
        lang_path = os.path.expanduser('~/tree-sitter-langs')
        Language.build_library(
            'build/ts_langs.dll',
            [
                f'{lang_path}/c',
                f'{lang_path}/cpp',
                f'{lang_path}/go'
            ]
        )
        
    def _init_parser(self, lang: str) -> Parser:
        language = Language('build/ts_langs.dll', lang)
        parser = Parser()
        parser.set_language(language)
        return parser
        
    def parse_code(self, code: str, lang: str) -> dict:
        """Return AST in json format"""
        tree = self.parsers[lang].parse(bytes(code, 'utf8'))
        return self._traverse_node(tree.root_node)
        
    def _traverse_node(self, node):
        return {
            'type': node.type,
            'start': {'line': node.start_point[0], 'column': node.start_point[1]},
            'end': {'line': node.end_point[0], 'column': node.end_point[1]},
            'children': [self._traverse_node(child) for child in node.children]
        }