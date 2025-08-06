"""
Query Engine for RAG System
Handles LLM interaction with Ollama and response generation
"""

import requests
import json
from typing import Dict, Any, Optional, List
from context_retriever import ContextRetriever
from vector_store import VectorStoreManager


class OllamaQueryEngine:
    """
    Query engine that uses Ollama for LLM inference with RAG context
    """
    
    def __init__(self, 
                 context_retriever: ContextRetriever,
                 model_name: str = "mistral:latest",
                 ollama_url: str = "http://localhost:11434",
                 system_prompt: str = None):
        """
        Initialize the query engine
        
        Args:
            context_retriever: ContextRetriever instance
            model_name: Name of the Ollama model
            ollama_url: URL of the Ollama server
            system_prompt: System prompt for the model
        """
        self.context_retriever = context_retriever
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        
        # Test connection
        self._test_ollama_connection()
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for financial Q&A"""
        return """You are a knowledgeable financial advisor assistant. Your task is to provide helpful, accurate, and practical financial advice based on the provided context.

Guidelines:
1. Answer questions based primarily on the provided context
2. Be clear and concise in your responses
3. If the context doesn't contain relevant information, say so clearly
4. Provide practical, actionable advice when possible
5. Always be professional and helpful
6. If you're uncertain about something, express that uncertainty
7. For financial topics, always remind users to consult with qualified professionals for personalized advice
8. You are not a licensed financial advisor, but you can provide general information and guidance based on the context provided.
9. Always consider the user's financial well-being and provide balanced, unbiased information.

Context Information:
The context provided contains information about various financial topics including self-employment, investments, tax implications, and financial planning. Use this information to provide relevant and helpful responses."""
    
    def _test_ollama_connection(self):
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model["name"] for model in models]
                
                if self.model_name not in model_names:
                    print(f"Warning: Model '{self.model_name}' not found in available models: {model_names}")
                    if model_names:
                        print(f"Available models: {model_names}")
                else:
                    print(f"Successfully connected to Ollama. Model '{self.model_name}' is available.")
            else:
                raise ConnectionError(f"Failed to connect to Ollama: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Cannot connect to Ollama at {self.ollama_url}: {str(e)}")
    
    def _build_prompt(self, query: str, context: str) -> str:
        """
        Build the complete prompt with context and query
        
        Args:
            query: User query
            context: Retrieved context
            
        Returns:
            Complete prompt string
        """
        prompt_template = f"""System: {self.system_prompt}

Context:
{context}

User Question: {query}

Please provide a helpful response based on the context above. If the context doesn't contain relevant information for the question, please say so clearly."""
        
        return prompt_template
    
    def _call_ollama(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> Dict[str, Any]:
        """
        Call Ollama API to generate response
        
        Args:
            prompt: Complete prompt to send
            temperature: Response randomness (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Prepare request payload
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            # Make request
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=120  # 2 minute timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "response": result.get("response", ""),
                    "done": result.get("done", False),
                    "context": result.get("context", []),
                    "eval_count": result.get("eval_count", 0),
                    "eval_duration": result.get("eval_duration", 0),
                    "total_duration": result.get("total_duration", 0)
                }
            else:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            raise TimeoutError("Request to Ollama timed out")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request to Ollama failed: {str(e)}")
    
    def query(self, 
              user_query: str, 
              k: int = 5,
              context_options: Dict[str, Any] = None,
              generation_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a user query with RAG
        
        Args:
            user_query: User's question
            k: Number of context chunks to retrieve
            context_options: Options for context retrieval
            generation_options: Options for text generation
            
        Returns:
            Dictionary with response and metadata
        """
        # Set defaults
        context_options = context_options or {}
        generation_options = generation_options or {}
        
        # Retrieve context
        print(f"Retrieving context for query: {user_query}")
        context_result = self.context_retriever.retrieve_context(
            user_query, 
            k=k,
            **context_options
        )
        
        if not context_result["context"]:
            return {
                "query": user_query,
                "response": "I couldn't find relevant information in the knowledge base to answer your question.",
                "context_used": "",
                "sources": [],
                "success": False,
                "error": "No relevant context found"
            }
        
        # Build prompt
        prompt = self._build_prompt(user_query, context_result["context"])
        
        # Generate response
        print("Generating response...")
        try:
            llm_result = self._call_ollama(prompt, **generation_options)
            
            return {
                "query": user_query,
                "response": llm_result["response"],
                "context_used": context_result["context"],
                "sources": context_result["sources"],
                "context_length": context_result["context_length"],
                "total_chunks": context_result["total_chunks"],
                "success": True,
                "generation_stats": {
                    "eval_count": llm_result.get("eval_count", 0),
                    "eval_duration": llm_result.get("eval_duration", 0),
                    "total_duration": llm_result.get("total_duration", 0)
                }
            }
            
        except Exception as e:
            return {
                "query": user_query,
                "response": f"Error generating response: {str(e)}",
                "context_used": context_result["context"],
                "sources": context_result["sources"],
                "success": False,
                "error": str(e)
            }
    
    def batch_query(self, 
                   queries: List[str], 
                   k: int = 5,
                   context_options: Dict[str, Any] = None,
                   generation_options: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Process multiple queries
        
        Args:
            queries: List of user queries
            k: Number of context chunks to retrieve
            context_options: Options for context retrieval
            generation_options: Options for text generation
            
        Returns:
            List of query results
        """
        results = []
        
        for i, query in enumerate(queries):
            print(f"Processing query {i+1}/{len(queries)}: {query}")
            result = self.query(query, k, context_options, generation_options)
            results.append(result)
        
        return results
    
    def interactive_session(self):
        """
        Start an interactive query session
        """
        print("Starting interactive RAG session...")
        print("Type 'exit' to quit, 'help' for commands")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() == 'exit':
                    print("Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    print("Available commands:")
                    print("  exit - Quit the session")
                    print("  help - Show this help message")
                    print("  Just type your question to get an answer")
                    continue
                
                if not user_input:
                    continue
                
                # Process query
                result = self.query(user_input)
                
                print(f"\nAssistant: {result['response']}")
                
                # Show sources if available
                if result.get('sources'):
                    print(f"\nSources used ({len(result['sources'])} chunks):")
                    for i, source in enumerate(result['sources'][:3]):  # Show top 3
                        print(f"  {i+1}. {source['source']} (Score: {source['similarity_score']:.3f})")
                
            except KeyboardInterrupt:
                print("\nSession interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model
        
        Returns:
            Dictionary with model information
        """
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if model["name"] == self.model_name:
                        return model
                return {"error": f"Model {self.model_name} not found"}
            else:
                return {"error": f"Failed to get model info: {response.status_code}"}
        except Exception as e:
            return {"error": f"Error getting model info: {str(e)}"}


# Convenience functions
def create_rag_system(force_recreate_db: bool = False) -> OllamaQueryEngine:
    """
    Create a complete RAG system with all components
    
    Args:
        force_recreate_db: Whether to recreate the vector database
        
    Returns:
        OllamaQueryEngine instance
    """
    from vector_store import create_vector_database
    from context_retriever import ContextRetriever
    
    # Create/load vector database
    print("Setting up vector database...")
    vector_manager = create_vector_database(force_recreate=force_recreate_db)
    
    # Create context retriever
    print("Setting up context retriever...")
    context_retriever = ContextRetriever(vector_manager)
    
    # Create query engine
    print("Setting up query engine...")
    query_engine = OllamaQueryEngine(context_retriever)
    
    print("RAG system ready!")
    return query_engine


if __name__ == "__main__":
    # Test the query engine
    try:
        # Create RAG system
        rag_system = create_rag_system()
        
        # Test queries
        test_queries = [
            "What are the tax implications of self-employment in the UK?",
            "How do I register as self-employed?",
            "What are the risks of investing in eToro?",
            "How can I diversify my investments?"
        ]
        
        print("Testing queries:")
        for query in test_queries:
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            print('='*60)
            
            result = rag_system.query(query)
            
            if result["success"]:
                print(f"Response: {result['response']}")
                print(f"Sources: {len(result['sources'])} chunks used")
                print(f"Context length: {result['context_length']} chars")
            else:
                print(f"Error: {result['error']}")
        
        # Start interactive session
        print(f"\n{'='*60}")
        print("Starting interactive session...")
        rag_system.interactive_session()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()