from tree_sitter import Node
from typing import List, Dict, Any
from pathlib import Path


class CodeAnalyzer:
    def __init__(self, parser):
        self.parser = parser
        self.current_file = None

    def analyze_node(self, node: Node, depth: int = 0) -> Dict[str, Any]:
        """Recursively analyze a node and its children."""
        result = {
            "type": node.type,
            "start_point": node.start_point,
            "end_point": node.end_point,
            "children": []
        }

        if node.type == "identifier":
            result["name"] = node.text.decode('utf8')

        for child in node.children:
            child_result = self.analyze_node(child, depth + 1)
            result["children"].append(child_result)

        return result

    def get_functions(self, tree: Node) -> List[Dict[str, Any]]:
        """Extract function definitions from the AST."""
        functions = []
        cursor = tree.walk()

        def visit_node():
            if cursor.node.type == "function_definition":
                name_node = cursor.node.child_by_field_name("name")
                if name_node:
                    functions.append({
                        "file": str(self.current_file),
                        "name": name_node.text.decode('utf8'),
                        "start_line": cursor.node.start_point[0],
                        "end_line": cursor.node.end_point[0]
                    })

            # Traverse children
            if cursor.goto_first_child():
                visit_node()
                while cursor.goto_next_sibling():
                    visit_node()
                cursor.goto_parent()

        visit_node()
        return functions

    def get_classes(self, tree: Node) -> List[Dict[str, Any]]:
        """Extract class definitions from the AST."""
        classes = []
        cursor = tree.walk()

        def visit_node():
            if cursor.node.type == "class_definition":
                name_node = cursor.node.child_by_field_name("name")
                if name_node:
                    class_info = {
                        "file": str(self.current_file),
                        "name": name_node.text.decode('utf8'),
                        "start_line": cursor.node.start_point[0],
                        "end_line": cursor.node.end_point[0],
                        "methods": []
                    }

                    # Get methods
                    for child in cursor.node.children:
                        if child.type == "function_definition":
                            method_name = child.child_by_field_name("name")
                            if method_name:
                                class_info["methods"].append(
                                    method_name.text.decode('utf8')
                                )

                    classes.append(class_info)

            # Traverse children
            if cursor.goto_first_child():
                visit_node()
                while cursor.goto_next_sibling():
                    visit_node()
                cursor.goto_parent()

        visit_node()
        return classes

    def get_imports(self, tree: Node) -> List[Dict[str, Any]]:
        """Extract import statements from the AST."""
        imports = []
        cursor = tree.walk()

        def visit_node():
            if cursor.node.type in ["import_statement", "import_from_statement"]:
                imports.append({
                    "file": str(self.current_file),
                    "type": cursor.node.type,
                    "text": cursor.node.text.decode('utf8'),
                    "line": cursor.node.start_point[0]
                })

            # Traverse children
            if cursor.goto_first_child():
                visit_node()
                while cursor.goto_next_sibling():
                    visit_node()
                cursor.goto_parent()

        visit_node()
        return imports

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Python file."""
        self.current_file = file_path

        tree = self.parser.parse_file(str(file_path))
        if not tree:
            raise RuntimeError(f"Failed to parse file: {file_path}")

        return {
            "file": str(file_path),
            "functions": self.get_functions(tree),
            "classes": self.get_classes(tree),
            "imports": self.get_imports(tree)
        }

    def analyze_relationships(self, file_paths: List[Path]) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze relationships between files."""
        relationships = {
            "function_calls": [],
            "class_inheritance": [],
            "import_dependencies": []
        }

        for file_path in file_paths:
            try:
                self.current_file = file_path
                tree = self.parser.parse_file(str(file_path))

                if not tree:
                    raise RuntimeError(f"Failed to parse file: {file_path}")

                # Analyze function calls
                self._analyze_function_calls(
                    tree, relationships["function_calls"])

                # Analyze class inheritance
                self._analyze_class_inheritance(
                    tree, relationships["class_inheritance"])

                # Analyze import dependencies
                self._analyze_import_dependencies(
                    tree, relationships["import_dependencies"])

            except Exception as e:
                print(
                    f"Error analyzing relationships in {file_path}: {str(e)}")

        return relationships

    def _analyze_function_calls(self, tree: Node, function_calls: List):
        """Analyze function calls within the AST."""
        cursor = tree.walk()
        current_function = None

        def visit_node():
            nonlocal current_function

            # Track current function context
            if cursor.node.type == "function_definition":
                name_node = cursor.node.child_by_field_name("name")
                if name_node:
                    current_function = name_node.text.decode('utf8')

            # Detect function calls
            if cursor.node.type == "call":
                function_name = cursor.node.child_by_field_name("function")
                if function_name and current_function:
                    callee = function_name.text.decode('utf8')
                    function_calls.append({
                        "file": str(self.current_file),
                        "caller": current_function,
                        "callee": callee,
                        "line": cursor.node.start_point[0]
                    })

            # Traverse children
            if cursor.goto_first_child():
                previous_function = current_function
                visit_node()
                while cursor.goto_next_sibling():
                    visit_node()
                cursor.goto_parent()
                current_function = previous_function

        visit_node()

    def _analyze_class_inheritance(self, tree: Node, class_inheritance: List):
        """Analyze class inheritance relationships."""
        cursor = tree.walk()

        def visit_node():
            if cursor.node.type == "class_definition":
                name_node = cursor.node.child_by_field_name("name")
                bases = cursor.node.child_by_field_name("bases")
                if name_node and bases:
                    class_name = name_node.text.decode('utf8')
                    for base in bases.children:
                        if base.type == "identifier":
                            class_inheritance.append({
                                "file": str(self.current_file),
                                "class": class_name,
                                "inherits_from": base.text.decode('utf8')
                            })

            if cursor.goto_first_child():
                visit_node()
                while cursor.goto_next_sibling():
                    visit_node()
                cursor.goto_parent()

        visit_node()

    def _analyze_import_dependencies(self, tree: Node, import_dependencies: List):
        """Analyze import dependencies between files."""
        cursor = tree.walk()

        def visit_node():
            if cursor.node.type in ["import_statement", "import_from_statement"]:
                import_path = cursor.node.text.decode('utf8')
                import_dependencies.append({
                    "file": str(self.current_file),
                    "import_statement": import_path,
                    "line": cursor.node.start_point[0]
                })

            if cursor.goto_first_child():
                visit_node()
                while cursor.goto_next_sibling():
                    visit_node()
                cursor.goto_parent()

        visit_node()
