"""
Setup and Run Script for RAG System
Handles initial setup, testing, and running the RAG system
"""

import os
import sys
import subprocess
import json
from main_rag import RAGSystem
from pathlib import Path
from document_loader import load_training_data


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print(" Python 3.8 or higher is required")
        return False
    print(f" Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def install_requirements():
    """Install required packages"""
    print(" Installing requirements...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print(" Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f" Failed to install requirements: {e}")
        return False


def check_ollama():
    """Check if Ollama is running"""
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f" Ollama is running with {len(models)} models")
            
            # Check if mistral is available
            model_names = [model["name"] for model in models]
            if "mistral:latest" in model_names:
                print(" Mistral model is available")
            else:
                print(" Mistral model not found. Available models:")
                for name in model_names:
                    print(f"   - {name}")
                print("Run: ollama pull mistral:latest")
            return True
        else:
            print(" Ollama is not responding properly")
            return False
    except Exception as e:
        print(f" Ollama is not running: {e}")
        print("Please start Ollama and run: ollama pull mistral:latest")
        return False


def run_rag_on_text(prompt: str, additional_context: str = "") -> str:
    """
    Entry point for external apps (FastAPI, AL) to query the RAG pipeline.
    Accepts a prompt and optional extra context.
    Returns AI-generated response.
    """
    print(f"[DEBUG] Prompt: {prompt[:100]}")
    print(f"[DEBUG] Context preview: {additional_context[:500]}")
    try:
        rag = RAGSystem()
        print("Training data exists:", os.path.exists("processed_data/training_data.json"))
        from document_loader import load_training_data

        try:
            docs = load_training_data("processed_data/training_data.json")
            print(f"Loaded {len(docs)} documents")
        except Exception as e:
            print("Error loading documents:", e)

        setup_success = rag.setup(force_recreate_db=False)

        if not setup_success:
            return "Failed to set up RAG system."

        full_prompt = f"{prompt}\n\nPDF Content:\n{additional_context}".strip()
        result = rag.query(full_prompt)

        if result.get("success"):
            return result.get("response", "No response generated.")
        else:
            return f"Query failed: {result.get('error', 'Unknown error')}"
    except Exception as e:
        return f"Exception during RAG run: {e}"

    

def main():
    """Main setup function"""
    print(" Setting up RAG System")
    print("=" * 50)
    # Ask if user wants to start interactive mode
    print("\nStart interactive mode now? (y/n): ", end="")
    rag = RAGSystem()
    rag.setup()
    rag.interactive_session()


if __name__ == "__main__":
    main()