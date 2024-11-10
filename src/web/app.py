from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import List
import tempfile
import json
import os

from analyzer.tree_parser import CodeParser
from analyzer.code_analyzer import CodeAnalyzer
from llm.gpt_client import GPTClient
from visualization.mermaid_generator import MermaidGenerator

# Initialize FastAPI app
app = FastAPI(title="Code Analysis Tool")

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR.parent.parent / "output"

# Create output directories if they don't exist
(OUTPUT_DIR / "questions").mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "diagrams").mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Initialize templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Initialize components
code_parser = CodeParser()
gpt_client = GPTClient()
mermaid_generator = MermaidGenerator()


@app.get("/")
async def index(request: Request):
    """Render the main page."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.post("/api/analyze")
async def analyze_files(files: List[UploadFile] = File(...)):
    try:
        results = {
            "files": [],
            "functions": [],
            "classes": [],
            "relationships": {},
            "imports": [],
            "errors": []
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            file_paths = []

            # Save uploaded files
            for file in files:
                if not file.filename.endswith('.py'):
                    continue

                # Create a proper filename in the temp directory
                file_path = Path(temp_dir) / file.filename
                content = await file.read()

                # Write the content properly
                with open(file_path, "wb") as f:
                    f.write(content)

                # Reset the file pointer for potential reuse
                await file.seek(0)

                file_paths.append(file_path)
                results["files"].append(file.filename)

            if not file_paths:
                raise HTTPException(
                    status_code=400,
                    detail="No Python files were uploaded"
                )

            # Initialize analyzer
            analyzer = CodeAnalyzer(code_parser)

            # Analyze each file
            for file_path in file_paths:
                try:
                    # Make sure to pass the Path object or string path, not the content
                    analysis = analyzer.analyze_file(file_path)
                    if "error" in analysis:
                        results["errors"].append({
                            "file": str(file_path),
                            "error": analysis["error"]
                        })
                        continue

                    results["functions"].extend(analysis.get("functions", []))
                    results["classes"].extend(analysis.get("classes", []))
                    results["imports"].extend(analysis.get("imports", []))
                except Exception as e:
                    results["errors"].append({
                        "file": str(file_path),
                        "error": str(e)
                    })

            # Analyze relationships between files
            try:
                results["relationships"] = analyzer.analyze_relationships(
                    file_paths)
            except Exception as e:
                results["errors"].append({
                    "component": "relationships",
                    "error": str(e)
                })

            return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ask-gpt")
async def ask_gpt(request: Request):
    try:
        data = await request.json()
        question = data["question"]
        context = data["context"]

        # Create a concise summary of the analysis
        summary = {
            "files": context["files"],
            "summary": {
                "total_functions": len(context["functions"]),
                "total_classes": len(context["classes"]),
                "total_imports": len(context["imports"])
            },
            "functions": [
                {
                    # Just the filename
                    "file": f.get("file", "").split('/')[-1],
                    "name": f.get("name", ""),
                    "lines": f"L{f.get('start_line', 0)}-{f.get('end_line', 0)}"
                }
                for f in context["functions"]
            ],
            "classes": [
                {
                    "file": c.get("file", "").split('/')[-1],
                    "name": c.get("name", ""),
                    "lines": f"L{c.get('start_line', 0)}-{c.get('end_line', 0)}",
                    "methods": c.get("methods", [])
                }
                for c in context["classes"]
            ],
            "imports": [
                {
                    "file": imp.get("file", "").split('/')[-1],
                    "import": imp.get("text", ""),
                    "line": imp.get("line", 0)
                }
                for imp in context["imports"]
            ]
        }

        # Convert to a more token-efficient string format
        context_str = f"""
        Analyzed Files: {', '.join(summary['files'])}

        Stats: {summary['summary']['total_functions']} functions, {summary['summary']['total_classes']} classes, {summary['summary']['total_imports']} imports

        Functions (file:name@lines):
        {chr(10).join(f"{f['file']}:{f['name']}@{f['lines']}" for f in summary['functions'])}

        Classes (file:name@lines [methods]):
        {chr(10).join(f"{c['file']}:{c['name']}@{c['lines']} [{','.join(c['methods'])}]" for c in summary['classes'])}

        Imports (file@line:import):
        {chr(10).join(f"{imp['file']}@L{imp['line']}:{imp['import']}" for imp in summary['imports'])}

        Relationships:
        {str(context.get('relationships', {}))}
        """

        # Get response from GPT
        response = gpt_client.ask_question(question, context_str)

        return {"answer": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-diagram")
async def generate_diagram(request: Request):
    try:
        data = await request.json()
        diagram_type = data["type"]
        analysis = data["analysis"]

        if diagram_type == "class":
            diagram = mermaid_generator.generate_diagram(analysis)
        else:
            diagram = mermaid_generator.generate_flowchart(analysis)

        return {"diagram": diagram}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/questions/{question_id}")
async def get_question_answer(question_id: int):
    """
    Get the answer to a specific question.

    Args:
        question_id: ID of the question (1-4)

    Returns:
        Question and answer as JSON
    """
    try:
        file_path = OUTPUT_DIR / "questions" / f"question_{question_id}.json"

        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Answer for question {question_id} not found"
            )

        with open(file_path, "r") as f:
            return json.load(f)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/diagram")
async def get_diagram():
    """
    Get the generated Mermaid diagram.

    Returns:
        Mermaid diagram markup
    """
    try:
        diagram_path = OUTPUT_DIR / "diagrams" / "codebase.mmd"

        if not diagram_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Diagram not found"
            )

        with open(diagram_path, "r") as f:
            return {"diagram": f.read()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": exc.status_code,
            "detail": exc.detail
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 500,
            "detail": "Internal server error"
        }
    )
