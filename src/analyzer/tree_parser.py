from tree_sitter import Language, Parser, Tree, Node
from typing import Optional, Callable
import os
from pathlib import Path
import subprocess


class CodeParser:
    def __init__(self):
        print("Initializing CodeParser...")
        self.parser: Optional[Parser] = None
        self.language: Optional[Language] = None
        self.setup_tree_sitter()
        print("Initialization complete.")

    def setup_tree_sitter(self) -> None:
        """Set up the tree-sitter parser with Python language support."""
        try:
            print("Setting up tree-sitter...")
            # Check if we need to clone the Python grammar
            if not os.path.exists('tree-sitter-python'):
                print("Cloning tree-sitter-python repository...")
                subprocess.run([
                    'git', 'clone',
                    'https://github.com/tree-sitter/tree-sitter-python.git'
                ], check=True)

            # Build the language library if it doesn't exist
            if not os.path.exists('build/my-languages.so'):
                print("Building language library...")
                os.makedirs('build', exist_ok=True)
                Language.build_library(
                    'build/my-languages.so',
                    ['tree-sitter-python']
                )

            # Load the Python language
            print("Loading Python language...")
            self.language = Language('build/my-languages.so', 'python')
            self.parser = Parser()
            self.parser.set_language(self.language)
            print("Tree-sitter setup complete.")

        except Exception as e:
            print(f"Error setting up tree-sitter: {str(e)}")
            raise

    def parse_file(self, file_path: str) -> Optional[Tree]:
        """
        Parse a Python file and return its syntax tree.
        """
        if not self.parser:
            raise RuntimeError("Parser not initialized")

        try:
            print(f"Parsing file: {file_path}")
            with open(file_path, 'rb') as f:
                content = f.read()
                print(f"File size: {len(content)} bytes")
                tree = self.parser.parse(content)
                print("File parsed successfully.")
                return tree
        except Exception as e:
            print(f"Error parsing file {file_path}: {str(e)}")
            return None

    def parse_source(self, source_code: str) -> Optional[Tree]:
        """
        Parse Python source code directly and return its syntax tree.
        """
        if not self.parser:
            raise RuntimeError("Parser not initialized")

        try:
            print("Parsing source code...")
            tree = self.parser.parse(bytes(source_code, 'utf8'))
            print("Source code parsed successfully.")
            return tree
        except Exception as e:
            print(f"Error parsing source code: {str(e)}")
            return None

    def get_root_node(self, tree: Tree) -> Optional[Node]:
        """
        Get the root node of a parsed syntax tree.
        """
        if tree:
            print("Retrieving root node...")
            return tree.root_node
        else:
            print("No tree provided.")
            return None

    def get_node_text(self, node: Node, source_code: bytes) -> str:
        """
        Get the text corresponding to a node in the syntax tree.
        """
        if node:
            print("Retrieving node text...")
            return node.text.decode('utf8')
        else:
            print("No node provided.")
            return ""
