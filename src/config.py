import os
from tree_sitter import Language, Parser
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    DEBUG: bool = False

    class Config:
        env_file = ".env"


settings = Settings()

# src/analyzer/tree_parser.py


class CodeParser:
    def __init__(self):
        # Build tree-sitter library
        Language.build_library(
            'build/my-languages.so',
            ['tree-sitter-python']
        )
        self.PY_LANGUAGE = Language('build/my-languages.so', 'python')
        self.parser = Parser()
        self.parser.set_language(self.PY_LANGUAGE)

    def parse_file(self, file_path: str):
        with open(file_path, 'rb') as f:
            tree = self.parser.parse(f.read())
            return tree

    def get_functions(self, tree):
        functions = []
        cursor = tree.walk()

        def walk_tree():
            if cursor.node.type == 'function_definition':
                functions.append({
                    'name': cursor.node.child_by_field_name('name').text.decode('utf8'),
                    'start_point': cursor.node.start_point,
                    'end_point': cursor.node.end_point
                })

            if cursor.goto_first_child():
                walk_tree()
                while cursor.goto_next_sibling():
                    walk_tree()
                cursor.goto_parent()

        walk_tree()
        return functions
