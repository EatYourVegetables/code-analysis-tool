from typing import Dict, Any


class MermaidGenerator:
    def __init__(self):
        self.nodes = set()
        self.relationships = []

    def generate_diagram(self, analysis_results: Dict[str, Any]) -> str:
        """Generate a Mermaid diagram from analysis results."""
        # Reset state
        self.nodes.clear()
        self.relationships.clear()

        # Build class diagram
        mermaid_code = ["classDiagram"]

        # Add classes
        for class_info in analysis_results["classes"]:
            class_name = class_info["name"]
            self.nodes.add(class_name)

            # Add class with methods
            methods = []
            for method in class_info["methods"]:
                methods.append(f"+{method}()")

            if methods:
                mermaid_code.append(f"class {class_name} {{")
                mermaid_code.extend(methods)
                mermaid_code.append("}")
            else:
                mermaid_code.append(f"class {class_name}")

        # Add inheritance relationships
        for inheritance in analysis_results["relationships"]["class_inheritance"]:
            child = inheritance["class"]
            parent = inheritance["inherits_from"]
            self.relationships.append(f"{child} --|> {parent}")

        # Add dependencies based on function calls
        for call in analysis_results["relationships"]["function_calls"]:
            if "caller_class" in call and "callee_class" in call:
                caller = call["caller_class"]
                callee = call["callee_class"]
                if caller != callee:
                    self.relationships.append(f"{caller} ..> {callee} : uses")

        # Add relationships to diagram
        mermaid_code.extend(self.relationships)

        return "\n".join(mermaid_code)

    def generate_flowchart(self, analysis_results: Dict[str, Any]) -> str:
        """Generate a Mermaid flowchart showing function calls."""
        mermaid_code = ["flowchart TD"]

        # Add nodes for functions
        for func in analysis_results["functions"]:
            func_id = f"func_{func['name']}"
            mermaid_code.append(f"{func_id}[\"{func['name']}\"]")

        # Add function call relationships
        for call in analysis_results["relationships"]["function_calls"]:
            caller = f"func_{call['caller']}"
            callee = f"func_{call['callee']}"
            mermaid_code.append(f"{caller} --> {callee}")

        return "\n".join(mermaid_code)
