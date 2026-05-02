import ast

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.imports = []
        self.functions = []
        self.classes = []

        self.is_entry_point = False
        self.has_wait_state = False

        self.decorators = set()

        self.inherited_classes = set()
        self.global_variables = set()

    def visit_Import(self, node):
        """
        Handels normal imports like "import sys" or "import sys, os"
        """
        for imports in node.names:
            self.imports.append(imports.name)

    def visit_ImportFrom(self, node):
        """
        Handle imports from a library like "from sys import argv"
        """
        # Safety fallback to handle relative imports like "from . import utils"
        module_name = node.module if node.module else ""

        for import_name in node.names:
            self.imports.append(f"{module_name}.{import_name.name}")

    def visit_FunctionDef(self, node):
        """
        Finds function names and decorators
        """
        self.functions.append(node.name)

        # Look for decorators used on function
        for decorator in node.decorator_list:
            # If the decorator is a Nme decorator then add the decorator name to the decorators set.
            if isinstance(decorator, ast.Name):
                self.decorators.add(decorator.id)
            # Else if the decorator is a Call and the called then we dig inside the function to get the name of the decorator.
            elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                self.decorators.add(decorator.func.id)

        # Look inside node for other nested nodes
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """
        Finds class names and inherited classes
        """
        self.classes.append(node.name)

        # Look for classes that this class inherits
        for inherited_class in node.bases:
            # If class name is inherited directly
            if isinstance(inherited_class, ast.Name):
                self.inherited_classes.add(inherited_class.id)

            # If module name is called before inherited class name
            elif isinstance(inherited_class, ast.Attribute):
                self.inherited_classes.add(inherited_class.attr)

            # If a function with a class is inherited
            elif isinstance(inherited_class, ast.Call) and isinstance(inherited_class.func, ast.Name):
                self.inherited_classes.add(inherited_class.func.id)

        self.generic_visit(node)

    def visit_Call(self, node):
        """
        Check if the name of a function matches the name of one of the waiting states functions
        """
        function_name = ""
        if isinstance(node.func, ast.Name):
            function_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            function_name = node.func.attr

        if function_name in [
            "listen", # for sockets
            "mainloop", # for tkinter
            "run", # for flask
            "run_forever", # for asyncio
            "serve_forever", # for http.server or socketserver libraries
        ]:
            self.has_wait_state = True

        self.generic_visit(node)

    def visit_If(self, node):
        """
        Looks for entry point if __name__ == "__main__" or if "__main__" == __name__
        """
        # Check if the "if" statement is a compare statement with two comparators
        if isinstance(node.test, ast.Compare) and len(node.test.comparators) == 1:

            # Take the left and the right side of the compare statement
            left_side = node.test.left
            right_side = node.test.comparators[0]

            # Checks if the compared values are the same to those compared in the entry point
            entry_point_variant_1 = (isinstance(left_side, ast.Name) and left_side.id == "__name__") and (isinstance(right_side, ast.Constant) and right_side.value == "__main__")
            entry_point_variant_2 = (isinstance(left_side, ast.Constant) and left_side.value == "__main__") and (isinstance(right_side, ast.Name) and right_side.id == "__name__")

            # If any entry point variable is true then this if statement represents an entrypoint
            if entry_point_variant_1 or entry_point_variant_2:
                self.is_entry_point = True

        self.generic_visit(node)

    def visit_Assign(self, node):
        if node.col_offset == 0:
            for variable in node.targets:
                if isinstance(variable, ast.Name):
                    self.global_variables.add(variable.id)
        self.generic_visit(node)



