from project_scanner import ProjectScanner
from parser import CodeParser
from analyzer import CodeAnalyzer

def main():
    # initialize
    scanner = ProjectScanner()
    parser = CodeParser()
    analyzer = CodeAnalyzer()
    
    # scan project
    project_path = r"C:\your\project\path"
    files = scanner.scan_project(project_path)
    
    # analyze files
    for lang, file_list in files.items():
        for file_path in file_list:
            code = scanner.get_file_content(file_path)
            ast = parser.parse_code(code, lang)
            analyzer.analyze_ast(ast, file_path, lang)
    
    # generate report
    report = analyzer.generate_report()
    print(f"Porject analysis report：")
    print(f"Total functions：{report['functions']}")
    print(f"Total Structs：{report['structs']}")
    print("\nDetails：")
    for name, items in report['details'].items():
        print(f"{name}: {len(items)}")

if __name__ == "__main__":
    main()