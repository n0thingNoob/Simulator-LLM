from tree_sitter import Language, Parser

Language.build_library(
    'build/go.so',
    ['vendor/tree-sitter-go']  # https://github.com/tree-sitter/tree-sitter-go
)

go_parser = Parser()
go_parser.set_language(Language('build/go.so'))