# src/main.py
import uvicorn
import os
from dotenv import load_dotenv


def setup_environment():
    """Setup environment variables and create necessary directories."""
    load_dotenv()

    # Create necessary directories
    os.makedirs("output/questions", exist_ok=True)
    os.makedirs("output/diagrams", exist_ok=True)

    # Ensure required environment variables are set
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}")


def main():
    """Main entry point for the application."""
    try:
        setup_environment()

        # Start the FastAPI server
        uvicorn.run(
            "src.web.app:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
