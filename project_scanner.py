import os
from pathlib import Path

class ProjectScanner:
    def __init__(self):
        self.supported_ext = {
            '.c': 'c',
            '.cpp': 'cpp', 
            '.h': 'cpp',
            '.hpp': 'cpp',
            '.go': 'go'
        }
        
    def scan_project(self, root_path: str) -> dict:
        """
        Return Structure:
        {
            'c': [file1.c, file2.c...],
            'cpp': [...],
            'go': [...]
        }
        """
        project_files = {lang: [] for lang in set(self.supported_ext.values())}
        
        for path in Path(root_path).rglob('*'):
            if path.is_file():
                ext = path.suffix.lower()
                if ext in self.supported_ext:
                    lang = self.supported_ext[ext]
                    project_files[lang].append(str(path))
                    
        return project_files

    def get_file_content(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()