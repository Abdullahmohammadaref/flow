import ast

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.imports = []
        self.functions = []
        self.classes = []
        self.decorators = set()
        self.is_entry_point = False
        self.has_wait_state = False