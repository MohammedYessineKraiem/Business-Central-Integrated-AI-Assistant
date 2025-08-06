"""
Context Retriever for RAG System
Handles document retrieval and context building
"""

from typing import List, Dict, Any, Optional
from langchain.docstore.document import Document
from vector_store import VectorStoreManager
import re


class ContextRetriever:
    """
    Retrieves relevant context for queries using vector similarity search
    """
    
    def __init__(self, vector_store_manager: VectorStoreManager):
        """
        Initialize the context retriever
        
        Args:
            vector_store_manager: VectorStoreManager instance
        """
        self.vector_store = vector_store_manager
        
    def retrieve_context(self, 
                        query: str, 
                        k: int = 5,
                        min_score_threshold: float = 0.0,
                        max_context_length: int = 4000,
                        include_metadata: bool = True) -> Dict[str, Any]:
        """
        Retrieve relevant context for a query
        
        Args:
            query: User query
            k: Number of documents to retrieve
            min_score_threshold: Minimum similarity score threshold
            max_context_length: Maximum total context length
            include_metadata: Whether to include metadata in response
            
        Returns:
            Dictionary containing context and metadata
        """
        # Get documents with similarity scores
        results = self.vector_store.similarity_search_with_score(query, k=k)
        
        # Filter by score threshold
        filtered_results = [
            (doc, score) for doc, score in results 
            if score >= min_score_threshold
        ]
        
        if not filtered_results:
            return {
                "context": "",
                "sources": [],
                "total_chunks": 0,
                "query": query,
                "message": "No relevant documents found"
            }
        
        # Build context
        context_parts = []
        sources = []
        current_length = 0
        
        for doc, score in filtered_results:
            content = doc.page_content.strip()
            
            # Check if adding this chunk would exceed max length
            if current_length + len(content) > max_context_length:
                # Try to fit partial content
                remaining_length = max_context_length - current_length
                if remaining_length > 100:  # Only add if we have decent space
                    content = content[:remaining_length].rsplit(' ', 1)[0] + "..."
                    context_parts.append(content)
                    current_length += len(content)
                break
            
            context_parts.append(content)
            current_length += len(content)
            
            # Collect source information
            source_info = {
                "chunk_id": doc.metadata.get('chunk_id', 'unknown'),
                "source": doc.metadata.get('source', 'unknown'),
                "category": doc.metadata.get('category', 'unknown'),
                "similarity_score": float(score),
                "chunk_size": len(content)
            }
            
            if include_metadata:
                source_info.update({
                    "parent_doc_id": doc.metadata.get('parent_doc_id', 'unknown'),
                    "chunk_index": doc.metadata.get('chunk_index', 0),
                    "total_chunks": doc.metadata.get('total_chunks', 1)
                })
            
            sources.append(source_info)
        
        # Join context parts
        context = "\n\n".join(context_parts)
        
        return {
            "context": context,
            "sources": sources,
            "total_chunks": len(context_parts),
            "query": query,
            "context_length": len(context),
            "max_context_length": max_context_length
        }
    
    def retrieve_filtered_context(self, 
                                 query: str, 
                                 category_filter: Optional[str] = None,
                                 source_filter: Optional[str] = None,
                                 k: int = 5,
                                 **kwargs) -> Dict[str, Any]:
        """
        Retrieve context with metadata filtering
        
        Args:
            query: User query
            category_filter: Filter by category
            source_filter: Filter by source
            k: Number of documents to retrieve
            **kwargs: Additional arguments for retrieve_context
            
        Returns:
            Dictionary containing filtered context and metadata
        """
        # Build filter dictionary
        filter_dict = {}
        if category_filter:
            filter_dict['category'] = category_filter
        if source_filter:
            filter_dict['source'] = source_filter
        
        # Get documents with filter
        if filter_dict:
            results = self.vector_store.similarity_search_with_score(
                query, k=k, filter_dict=filter_dict
            )
        else:
            results = self.vector_store.similarity_search_with_score(query, k=k)
        
        # Process results similar to retrieve_context
        filtered_results = [(doc, score) for doc, score in results]
        
        if not filtered_results:
            return {
                "context": "",
                "sources": [],
                "total_chunks": 0,
                "query": query,
                "filters_applied": filter_dict,
                "message": f"No relevant documents found with filters: {filter_dict}"
            }
        
        # Use the main retrieve_context logic but with filtered results
        context_parts = []
        sources = []
        current_length = 0
        max_context_length = kwargs.get('max_context_length', 4000)
        
        for doc, score in filtered_results:
            content = doc.page_content.strip()
            
            if current_length + len(content) > max_context_length:
                remaining_length = max_context_length - current_length
                if remaining_length > 100:
                    content = content[:remaining_length].rsplit(' ', 1)[0] + "..."
                    context_parts.append(content)
                    current_length += len(content)
                break
            
            context_parts.append(content)
            current_length += len(content)
            
            source_info = {
                "chunk_id": doc.metadata.get('chunk_id', 'unknown'),
                "source": doc.metadata.get('source', 'unknown'),
                "category": doc.metadata.get('category', 'unknown'),
                "similarity_score": float(score),
                "chunk_size": len(content)
            }
            
            sources.append(source_info)
        
        context = "\n\n".join(context_parts)
        
        return {
            "context": context,
            "sources": sources,
            "total_chunks": len(context_parts),
            "query": query,
            "context_length": len(context),
            "filters_applied": filter_dict,
            "max_context_length": max_context_length
        }
    
    def get_diverse_context(self, 
                           query: str, 
                           k: int = 10,
                           diversity_threshold: float = 0.7,
                           **kwargs) -> Dict[str, Any]:
        """
        Retrieve diverse context by avoiding very similar chunks
        
        Args:
            query: User query
            k: Number of documents to retrieve initially
            diversity_threshold: Similarity threshold for diversity
            **kwargs: Additional arguments for retrieve_context
            
        Returns:
            Dictionary containing diverse context and metadata
        """
        # Get more documents initially
        results = self.vector_store.similarity_search_with_score(query, k=k)
        
        if not results:
            return {
                "context": "",
                "sources": [],
                "total_chunks": 0,
                "query": query,
                "message": "No relevant documents found"
            }
        
        # Simple diversity filtering - avoid chunks with high content overlap
        diverse_results = []
        seen_contents = []
        
        for doc, score in results:
            content = doc.page_content.strip()
            
            # Check similarity with already selected content
            is_diverse = True
            for seen_content in seen_contents:
                # Simple overlap check
                overlap = self._calculate_text_overlap(content, seen_content)
                if overlap > diversity_threshold:
                    is_diverse = False
                    break
            
            if is_diverse:
                diverse_results.append((doc, score))
                seen_contents.append(content)
        
        # Limit to reasonable number
        diverse_results = diverse_results[:5]
        
        # Build context from diverse results
        context_parts = []
        sources = []
        current_length = 0
        max_context_length = kwargs.get('max_context_length', 4000)
        
        for doc, score in diverse_results:
            content = doc.page_content.strip()
            
            if current_length + len(content) > max_context_length:
                remaining_length = max_context_length - current_length
                if remaining_length > 100:
                    content = content[:remaining_length].rsplit(' ', 1)[0] + "..."
                    context_parts.append(content)
                    current_length += len(content)
                break
            
            context_parts.append(content)
            current_length += len(content)
            
            source_info = {
                "chunk_id": doc.metadata.get('chunk_id', 'unknown'),
                "source": doc.metadata.get('source', 'unknown'),
                "category": doc.metadata.get('category', 'unknown'),
                "similarity_score": float(score),
                "chunk_size": len(content)
            }
            
            sources.append(source_info)
        
        context = "\n\n".join(context_parts)
        
        return {
            "context": context,
            "sources": sources,
            "total_chunks": len(context_parts),
            "query": query,
            "context_length": len(context),
            "diversity_applied": True,
            "max_context_length": max_context_length
        }
    
    def _calculate_text_overlap(self, text1: str, text2: str) -> float:
        """
        Calculate simple text overlap ratio
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Overlap ratio (0-1)
        """
        # Simple word-based overlap
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def search_by_keywords(self, 
                          keywords: List[str], 
                          k: int = 5,
                          **kwargs) -> Dict[str, Any]:
        """
        Search for context using specific keywords
        
        Args:
            keywords: List of keywords to search for
            k: Number of documents to retrieve
            **kwargs: Additional arguments for retrieve_context
            
        Returns:
            Dictionary containing keyword-based context
        """
        # Create query from keywords
        query = " ".join(keywords)
        
        # Get context
        context_result = self.retrieve_context(query, k=k, **kwargs)
        
        # Add keyword information
        context_result["keywords_used"] = keywords
        context_result["search_type"] = "keyword_based"
        
        return context_result
    
    def get_context_summary(self, context_result: Dict[str, Any]) -> str:
        """
        Generate a summary of the retrieved context
        
        Args:
            context_result: Result from retrieve_context
            
        Returns:
            Summary string
        """
        if not context_result.get("context"):
            return "No context retrieved"
        
        summary_parts = [
            f"Query: {context_result['query']}",
            f"Retrieved {context_result['total_chunks']} relevant chunks",
            f"Total context length: {context_result['context_length']} characters"
        ]
        
        if context_result.get("sources"):
            sources_by_category = {}
            for source in context_result["sources"]:
                category = source.get("category", "unknown")
                if category not in sources_by_category:
                    sources_by_category[category] = 0
                sources_by_category[category] += 1
            
            summary_parts.append(f"Sources by category: {sources_by_category}")
        
        return "\n".join(summary_parts)


# Convenience functions
def create_context_retriever(vector_store_manager: VectorStoreManager = None) -> ContextRetriever:
    """
    Create a context retriever with default vector store
    
    Args:
        vector_store_manager: Optional VectorStoreManager instance
        
    Returns:
        ContextRetriever instance
    """
    if vector_store_manager is None:
        from vector_store import VectorStoreManager
        vector_store_manager = VectorStoreManager()
        vector_store_manager.load_vectorstore()
    
    return ContextRetriever(vector_store_manager)


if __name__ == "__main__":
    # Test the context retriever
    try:
        from vector_store import VectorStoreManager
        
        # Load vector store
        manager = VectorStoreManager()
        manager.load_vectorstore()
        
        # Create retriever
        retriever = ContextRetriever(manager)
        
        # Test queries
        test_queries = [
            "What are the tax implications of self-employment?",
            "How do I register as self-employed in the UK?",
            "What are the risks of eToro investments?",
            "How to diversify investments with ETFs?"
        ]
        
        for query in test_queries:
            print(f"\n{'='*50}")
            print(f"Testing query: {query}")
            print('='*50)
            
            # Get context
            context_result = retriever.retrieve_context(query, k=3)
            
            # Print summary
            print(retriever.get_context_summary(context_result))
            
            # Print first source
            if context_result["sources"]:
                first_source = context_result["sources"][0]
                print(f"\nTop result (Score: {first_source['similarity_score']:.4f}):")
                print(f"Source: {first_source['source']}")
                print(f"Category: {first_source['category']}")
                print(f"Preview: {context_result['context'][:200]}...")
        
        # Test filtered search
        print(f"\n{'='*50}")
        print("Testing filtered search")
        print('='*50)
        
        filtered_result = retriever.retrieve_filtered_context(
            "tax implications", 
            category_filter="financial_qa",
            k=2
        )
        
        print(retriever.get_context_summary(filtered_result))
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()