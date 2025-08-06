"""
Main RAG System - Complete Financial Q&A Assistant
Integrates all components: document loading, chunking, vector storage, and query processing
"""

import os
import sys
import argparse
from typing import Dict, Any, List, Optional
from pathlib import Path

# Import all components
from document_loader import load_training_data
from chunking_processor import process_training_data
from vector_store import VectorStoreManager, create_vector_database
from context_retriever import ContextRetriever
from code_engine import OllamaQueryEngine


class RAGSystem:
    """
    Complete RAG System for Financial Q&A
    """
    
    def __init__(self, 
                 data_path: str = "processed_data/training_data.json",
                 vector_db_path: str = "chroma_db",
                 model_name: str = "mistral:latest",
                 ollama_url: str = "http://127.0.0.1:11434"):
        """
        Initialize the RAG system
        
        Args:
            data_path: Path to training data JSON file
            vector_db_path: Path to ChromaDB storage
            model_name: Ollama model name
            ollama_url: Ollama server URL
        """
        self.data_path = data_path
        self.vector_db_path = vector_db_path
        self.model_name = model_name
        self.ollama_url = ollama_url
        
        # Components
        self.vector_manager = None
        self.context_retriever = None
        self.query_engine = None
        
        # Status
        self.is_initialized = False
    
    def setup(self, force_recreate_db: bool = False, 
          chunk_size: int = 1000, 
          chunk_overlap: int = 200) -> bool:
        """
        Set up the complete RAG system
        
        Args:
            force_recreate_db: Whether to recreate the vector database
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            True if setup successful, False otherwise
        """
        try:
            print(" Setting up RAG system...")
            
            # Step 1: Check data file exists
            if not os.path.exists(self.data_path):
                print(f" Error: Training data file not found at {self.data_path}")
                return False
            
            # Step 2: Create or load vector database
            print(" Setting up vector database...")
            self.vector_manager = VectorStoreManager(
                persist_directory=self.vector_db_path
            )
            
            if force_recreate_db:
                print("Force recreate requested: deleting existing vector store...")
                self.vector_manager.delete_collection()
                print("Creating new vector database...")
                self._create_new_database(chunk_size, chunk_overlap)
            else:
                print("Attempting to load existing vector store...")
                existing_db = self.vector_manager.load_vectorstore()
                if existing_db:
                    print("Using existing vector database")
                else:
                    print("Existing vector store missing or incomplete, deleting and recreating...")
                    self.vector_manager.delete_collection()
                    self._create_new_database(chunk_size, chunk_overlap)
            
            # Step 3: Set up context retriever
            print("🔍 Setting up context retriever...")
            self.context_retriever = ContextRetriever(self.vector_manager)
            
            # Step 4: Set up query engine
            print("🤖 Setting up query engine...")
            self.query_engine = OllamaQueryEngine(
                context_retriever=self.context_retriever,
                model_name=self.model_name,
                ollama_url=self.ollama_url
            )
            
            self.is_initialized = True
            print("RAG system setup complete!")
            return True
            
        except Exception as e:
            print(f"Error setting up RAG system: {str(e)}")
            return False

    
    def _create_new_database(self, chunk_size: int, chunk_overlap: int):
        """Create new vector database from training data"""
        # Load and process training data
        print("Loading training data...")
        documents = load_training_data(self.data_path)
        
        if not documents:
            raise ValueError("No documents loaded from training data")
        
        print(f"Loaded {len(documents)} documents")
        
        # Process into chunks
        print(" Processing documents into chunks...")
        from chunking_processor import DocumentChunkProcessor
        
        processor = DocumentChunkProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        chunks = processor.process_documents(documents)
        
        if not chunks:
            raise ValueError("No chunks created from documents")
        
        print(f" Created {len(chunks)} chunks")
        
        # Create vector store
        print(" Creating embeddings and vector store...")
        self.vector_manager.create_vectorstore(chunks)
        
        # Get statistics
        stats = self.vector_manager.get_collection_stats()
        print(f" Vector store statistics:")
        print(f"   Total documents: {stats.get('total_documents', 0)}")
        print(f"   Embedding model: {stats.get('embedding_model', 'unknown')}")
    
    def query(self, question: str, **kwargs) -> Dict[str, Any]:
        """
        Query the RAG system
        
        Args:
            question: User question
            **kwargs: Additional options for query processing
            
        Returns:
            Dictionary with response and metadata
        """
        if not self.is_initialized:
            return {
                "error": "RAG system not initialized. Call setup() first.",
                "success": False
            }
        
        try:
            result = self.query_engine.query(question, **kwargs)
            return result
            
        except Exception as e:
            return {
                "query": question,
                "error": f"Error processing query: {str(e)}",
                "success": False
            }
    
    def batch_query(self, questions: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Process multiple queries
        
        Args:
            questions: List of questions
            **kwargs: Additional options
            
        Returns:
            List of query results
        """
        if not self.is_initialized:
            return [{"error": "RAG system not initialized", "success": False}] * len(questions)
        
        return self.query_engine.batch_query(questions, **kwargs)
    
    def interactive_session(self):
        """Start interactive Q&A session"""
        if not self.is_initialized:
            print(" RAG system not initialized. Call setup() first.")
            return
        
        print(" Starting interactive RAG session...")
        print("Commands: 'exit' to quit, 'help' for help, 'stats' for system info")
        print("-" * 60)
        
        while True:
            try:
                user_input = input("\n You: ").strip()
                
                if user_input.lower() == 'exit':
                    print(" Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if user_input.lower() == 'stats':
                    self._show_stats()
                    continue
                
                if not user_input:
                    continue
                
                # Process query
                print("🔍 Searching knowledge base...")
                result = self.query(user_input)
                
                if result["success"]:
                    print(f"\n Assistant: {result['response']}")
                    
                    # Show sources
                    if result.get('sources'):
                        print(f"\n📚 Sources ({len(result['sources'])} chunks):")
                        for i, source in enumerate(result['sources'][:3]):
                            score = source['similarity_score']
                            category = source['category']
                            print(f"   {i+1}. {category} (relevance: {score:.3f})")
                else:
                    print(f" Error: {result['error']}")
                
            except KeyboardInterrupt:
                print("\n Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f" Error: {str(e)}")
    
    def _show_help(self):
        """Show help information"""
        print("\nAvailable commands:")
        print("  exit  - Quit the session")
        print("  help  - Show this help message")
        print("  stats - Show system statistics")
        print("  Just type your financial question to get an answer!")
    
    def _show_stats(self):
        """Show system statistics"""
        if not self.is_initialized:
            print(" System not initialized")
            return
        
        print("\n System Statistics:")
        
        # Vector store stats
        if self.vector_manager:
            stats = self.vector_manager.get_collection_stats()
            print(f" Vector Database:")
            print(f"   Documents: {stats.get('total_documents', 0)}")
            print(f"   Collection: {stats.get('collection_name', 'unknown')}")
            print(f"   Embedding model: {stats.get('embedding_model', 'unknown')}")
        
        # Model info
        if self.query_engine:
            model_info = self.query_engine.get_model_info()
            print(f" LLM Model:")
            print(f"   Name: {self.model_name}")
            print(f"   Status: {'Available' if not model_info.get('error') else 'Error'}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information
        
        Returns:
            Dictionary with system information
        """
        info = {
            "initialized": self.is_initialized,
            "data_path": self.data_path,
            "vector_db_path": self.vector_db_path,
            "model_name": self.model_name,
            "ollama_url": self.ollama_url
        }
        
        if self.is_initialized:
            if self.vector_manager:
                info["vector_store_stats"] = self.vector_manager.get_collection_stats()
            
            if self.query_engine:
                info["model_info"] = self.query_engine.get_model_info()
        
        return info


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="Financial Q&A RAG System")
    parser.add_argument("--data-path", default="processed_data/training_data.json",
                       help="Path to training data JSON file")
    parser.add_argument("--vector-db-path", default="chroma_db",
                       help="Path to ChromaDB storage")
    parser.add_argument("--model-name", default="mistral:latest",
                       help="Ollama model name")
    parser.add_argument("--ollama-url", default="http://localhost:11434",
                       help="Ollama server URL")
    parser.add_argument("--recreate-db", action="store_true",
                       help="Force recreate vector database")
    parser.add_argument("--chunk-size", type=int, default=1000,
                       help="Text chunk size")
    parser.add_argument("--chunk-overlap", type=int, default=200,
                       help="Chunk overlap size")
    parser.add_argument("--query", type=str,
                       help="Single query to process")
    parser.add_argument("--batch-queries", type=str,
                       help="File with queries to process in batch")
    
    args = parser.parse_args()
    
    # Create RAG system
    rag = RAGSystem(
        data_path=args.data_path,
        vector_db_path=args.vector_db_path,
        model_name=args.model_name,
        ollama_url=args.ollama_url
    )
    
    # Setup system
    print("Initializing RAG system...")
    success = rag.setup(
        force_recreate_db=args.recreate_db,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )
    
    if not success:
        print(" Failed to initialize RAG system")
        sys.exit(1)
    
    # Handle different modes
    if args.query:
        # Single query mode
        print(f"\n Processing query: {args.query}")
        result = rag.query(args.query)
        
        if result["success"]:
            print(f"\n Response: {result['response']}")
            print(f" Used {len(result.get('sources', []))} source chunks")
        else:
            print(f" Error: {result['error']}")
    
    elif args.batch_queries:
        # Batch query mode
        if not os.path.exists(args.batch_queries):
            print(f" Batch queries file not found: {args.batch_queries}")
            sys.exit(1)
        
        with open(args.batch_queries, 'r') as f:
            queries = [line.strip() for line in f if line.strip()]
        
        print(f"\n Processing {len(queries)} queries...")
        results = rag.batch_query(queries)
        
        for i, result in enumerate(results):
            print(f"\n--- Query {i+1} ---")
            print(f"Q: {result['query']}")
            if result["success"]:
                print(f"A: {result['response']}")
            else:
                print(f"Error: {result['error']}")
    
    else:
        # Interactive mode
        rag.interactive_session()


if __name__ == "__main__":
    main()