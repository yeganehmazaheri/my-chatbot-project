import re

class DocumentDatabase:
    def __init__(self, document_file='answers.txt'):
        self.document_file = document_file
        self.sections = self._load_and_split_document()
        
    def _load_and_split_document(self):
        """Load the document and split into sections based on English format"""
        try:
            with open(self.document_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: File {self.document_file} not found.")
            return []
        
        # Optimized: Split by headings followed by 'Description:'
        pattern = r'(.*\n)\nDescription:'
        sections = re.split(pattern, content)
        
        structured_sections = []
        
        for i in range(1, len(sections), 2):
            if i+1 < len(sections):
                heading = sections[i].strip()
                content = sections[i+1].strip()  # No need to add back, as it's after Description:
                structured_sections.append((heading, content))
        
        if not structured_sections:
            structured_sections.append(("Savin Chimie Hormoz Company Document", content))
        
        return structured_sections
    
    def get_all_sections(self):
        return self.sections
    
    def get_document_text(self):
        return "\n".join([f"{heading}\nDescription: {content}" for heading, content in self.sections])