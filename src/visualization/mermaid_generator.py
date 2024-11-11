from typing import Dict, Any, Set, List
from pathlib import Path


class MermaidGenerator:
    def __init__(self):
        self.nodes = set()
        self.connections = set()
        self.file_mapping = {}
        self.descriptions = {
            'ask_api': 'Web interface using Gradio\nMakes HTTP requests to API\nendpoints',
            'ask_url': 'Entry point for URL-based PDF\nprocessing\nHandles URL submissions',
            'ask_file': 'Entry point for direct file uploads\nHandles file submissions',
            'download_pdf': 'Downloads PDF from URL using\nurllib',
            'generate_answer': 'Core function that generates\nanswer using context',
            'generate_text': 'Generates text using LiteLLM\ncompletion',
            'load_openai_key': 'Loads OpenAI API key from\nenvironment',
            'load_recommender': 'Initializes semantic search system',
            'pdf_to_text': 'Converts PDF to text using\nPyMuPDF',
            'text_to_chunks': 'Splits text into manageable chunks',
            'preprocess': 'Cleans and normalizes text',
            'fit': 'Trains semantic search model\non document chunks',
            'get_text_embedding': 'Generates embeddings for\ntext using USE model'
        }

    def process_analysis_data(self, analysis_data):
        # Track functions by file
        for func in analysis_data.get('functions', []):
            if not func['name'].startswith('__'):
                file = 'api.py' if 'api.py' in func['file'] else 'app.py'
                self.file_mapping[func['name']] = file
                self.nodes.add(func['name'])

        # Process function calls
        function_calls = analysis_data.get(
            'relationships', {}).get('function_calls', [])
        for call in function_calls:
            caller = call.get('caller')
            callee = call.get('callee')

            if (caller and callee and
                not caller.startswith('__') and
                not callee.startswith('_') and
                    not any(x in callee for x in ['.', 'print', 'str', 'len'])):

                # Add relationship for semantic search internals
                if caller == 'fit' or callee == 'fit' or \
                   caller == 'get_text_embedding' or callee == 'get_text_embedding':
                    self.connections.add((caller, callee))
                elif callee in self.file_mapping.keys():
                    self.connections.add((caller, callee))

        # Add explicit app->api relationships
        if 'ask_api' in self.nodes:
            self.connections.add(('ask_api', 'ask_url'))
            self.connections.add(('ask_api', 'ask_file'))

        # Add semantic search relationships
        self.connections.add(('load_recommender', 'fit'))
        self.connections.add(('fit', 'get_text_embedding'))

    def generate_mermaid(self):
        """Generate Mermaid flowchart code with subgraphs and tooltips."""
        lines = ["flowchart TD"]

        # Add app.py subgraph
        lines.append('    subgraph APP[app.py]')
        for node in sorted(n for n in self.nodes if self.file_mapping.get(n) == 'app.py'):
            desc = self.descriptions.get(node, '').replace('\n', '<br>')
            lines.append(
                f'        {node}["{node}<br><small>{desc}</small>"]:::interface')
        lines.append('    end')

        # Add api.py subgraph
        lines.append('    subgraph API[api.py]')
        # Entry points
        for node in sorted(n for n in ['ask_url', 'ask_file'] if n in self.nodes):
            desc = self.descriptions.get(node, '').replace('\n', '<br>')
            lines.append(
                f'        {node}["{node}<br><small>{desc}</small>"]:::entryPoint')

        # Core functions
        for node in sorted(n for n in ['generate_answer', 'generate_text'] if n in self.nodes):
            desc = self.descriptions.get(node, '').replace('\n', '<br>')
            lines.append(
                f'        {node}["{node}<br><small>{desc}</small>"]:::core')

        # Utility functions including semantic search
        for node in sorted(n for n in self.nodes if n not in ['ask_api', 'ask_url', 'ask_file', 'generate_answer', 'generate_text']
                           and self.file_mapping.get(n) == 'api.py'):
            desc = self.descriptions.get(node, '').replace('\n', '<br>')
            lines.append(
                f'        {node}["{node}<br><small>{desc}</small>"]:::utility')
        lines.append('    end')

        # Add connections
        for caller, callee in sorted(self.connections):
            if self.file_mapping.get(caller) != self.file_mapping.get(callee):
                lines.append(f"    {caller} -.-> {callee}")
            else:
                lines.append(f"    {caller} --> {callee}")

        # Add styling
        lines.extend([
            "    classDef interface fill:#E1BEE7,stroke:#4A148C,stroke-width:2px",
            "    classDef entryPoint fill:#90CAF9,stroke:#0D47A1,stroke-width:2px",
            "    classDef core fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px",
            "    classDef utility fill:#FFF59D,stroke:#F57F17,stroke-width:1px",
            "    style API fill:#f8f9fa,stroke:#666,stroke-width:2px",
            "    style APP fill:#f8f9fa,stroke:#666,stroke-width:2px"
        ])

        return "\n".join(lines)

    def create_flowchart(self, analysis_data):
        self.process_analysis_data(analysis_data)
        return self.generate_mermaid()
