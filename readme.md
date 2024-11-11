# Code Analysis Tool

A web-based Python code analysis tool that uses Tree-sitter for parsing and GPT-4 for intelligent code analysis.

## Features

- 📊 Real-time code analysis and visualization
- 🤖 GPT-4 powered code insights
- 📈 Interactive Mermaid diagrams
- 🌲 AST-based code parsing
- 🔍 Cross-file relationship analysis
- 📱 Modern, responsive UI

## Prerequisites

- Python 3.11+

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/code-analysis-tool.git
cd code-analysis-tool
```

2. Create and activate a Python virtual environment:

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

4. Set up environment variables by creating a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key
DEBUG=False
```

## Environment Variables

| Variable       | Description         | Required | Default |
| -------------- | ------------------- | -------- | ------- |
| OPENAI_API_KEY | Your OpenAI API key | Yes      | -       |

## Running the Application

1. Start the FastAPI server:

```bash
python main.py
```

2. Open your browser and navigate to:

```
http://localhost:8000
```

## Usage Examples

### 1. Basic Code Analysis

1. Open the web interface
2. Drag and drop Python files or click to select them
3. Wait for the analysis to complete
4. View the results in the different tabs:
   - Functions
   - Classes
   - Relationships
   - Imports

### 2. Using GPT Analysis

1. Complete a code analysis
2. Scroll to the "Ask Questions About Your Code" section
3. Enter your question
4. View the AI-generated response

### 3. Generating Diagrams

1. Complete a code analysis
2. Click the "Generate Diagram" button
3. View the interactive diagram
4. Use zoom controls to explore
5. Download as SVG if needed

## Project Structure

```
code-analysis-tool/
├── src/
│   ├── analyzer/
│   │   ├── code_analyzer.py
│   │   └── tree_parser.py
│   ├── llm/
│   │   └── gpt_client.py
│   ├── visualization/
│   │   └── mermaid_generator.py
│   └── web/
│       ├── static/
│       ├── templates/
│       └── app.py
├── main.py
└── config.py
```

## Troubleshooting Guide

### Common Issues

1. **Tree-sitter Installation Fails**

   ```bash
   # Solution 1: Install build tools
   # Windows
   npm install -g windows-build-tools
   # Linux
   sudo apt-get install build-essential

   # Solution 2: Manual installation
   git clone https://github.com/tree-sitter/tree-sitter-python.git
   cd tree-sitter-python
   ```

2. **OpenAI API Key Issues**

   - Verify the key is correctly set in .env
   - Check for leading/trailing whitespace
   - Ensure the key has proper permissions

3. **File Upload Fails**

   - Check file size (limit: 10MB)
   - Ensure files are .py extension
   - Clear browser cache
   - Try uploading fewer files

4. **Diagram Generation Issues**
   - Check browser console for errors
   - Try reducing code complexity
   - Clear browser cache
   - Update Mermaid.js if needed

### Error Messages and Solutions

| Error                  | Cause                 | Solution                  |
| ---------------------- | --------------------- | ------------------------- |
| "Failed to parse file" | Invalid Python syntax | Check file contents       |
| "API key invalid"      | Incorrect OpenAI key  | Verify .env file          |
| "File too large"       | >10MB file            | Split file or reduce size |

## Development

### Setting up a Development Environment

1. Clone the repository
2. Create a virtual environment
3. Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

### Running Tests

```bash
pytest tests/
```

### Code Style

- Follow PEP 8
- Use type hints
- Document functions
- Keep functions small and focused

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Support

For support, please:

1. Check the troubleshooting guide
2. Search existing issues
3. Create a new issue with:
   - Error message
   - Steps to reproduce
   - Environment details
