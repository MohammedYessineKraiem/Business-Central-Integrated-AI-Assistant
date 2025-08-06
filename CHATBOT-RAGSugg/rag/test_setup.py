from main_rag import RAGSystem

def test_rag_setup():
    rag = RAGSystem(
        data_path="processed_data/training_data.json",
        vector_db_path="chroma_db",
        model_name="mistral:latest",
        ollama_url="http://127.0.0.1:11434"
    )
    
    success = rag.setup(force_recreate_db=False, chunk_size=1000, chunk_overlap=200)
    
    if success:
        print("RAG system setup succeeded!")
    else:
        print("RAG system setup failed!")

if __name__ == "__main__":
    test_rag_setup()
