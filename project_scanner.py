# project_scanner.py
def scan_project(project_path: str) -> dict:
    summary = {
        'total_files': 0,
        'structs': defaultdict(int),
        'functions': defaultdict(int)
    }
    
    for root, _, files in os.walk(project_path):
        for file in files:
            if not file.endswith('.go'):
                continue
            
            file_path = os.path.join(root, file)
            analysis = analyze_go_file(file_path)
            
            summary['total_files'] += 1
            summary['structs'][file] = len(analysis['structs'])
            summary['functions'][file] = len(analysis['functions'])
    
    return summary