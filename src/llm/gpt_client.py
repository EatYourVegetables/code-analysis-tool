from pathlib import Path
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException, UploadFile, File
from openai import OpenAI
from config import settings


class GPTClient:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def ask_question(self, question: str, context: str) -> str:
        try:
            system_prompt = """You are an expert code analysis assistant. You analyze Python code and provide detailed, 
            accurate answers about code structure, relationships, and patterns. When referencing specific parts of the code, 
            use precise references including file names and line numbers. Focus on providing practical, technically accurate 
            insights based on the code analysis provided."""

            user_prompt = f"""
            Analysis of Python codebase:

            The following is a detailed analysis of the Python code:
            {context}

            Please analyze this information and answer the following question:
            {question}

            When referencing specific code elements:
            - Include the file name and line numbers
            - Mention relationships between components if relevant
            - Be specific about imports and dependencies
            - Reference concrete examples from the code
            """

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                seed=0
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"


# src/web/app.py

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

# Templates
templates = Jinja2Templates(directory="src/web/templates")

# Routes will be added here
