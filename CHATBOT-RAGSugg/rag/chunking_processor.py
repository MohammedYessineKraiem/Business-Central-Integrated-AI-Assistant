"""
Document Chunking Processor for RAG System
Handles text splitting and chunking using LangChain
"""

from typing import List, Dict, Any
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from document_loader import load_training_data


class DocumentChunkProcessor:
    """
    Process documents into chunks for RAG system
    """
    
    def __init__(self, 
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 separators: List[str] = None):
        """
        Initialize the chunk processor
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks
            separators: List of separators for splitting
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Default separators optimized for Q&A and instruction content
        if separators is None:
            separators = [
                "\n\n",  # Paragraph breaks
                "\n",    # Line breaks
                ". ",    # Sentence endings
                "! ",    # Exclamation endings
                "? ",    # Question endings
                "; ",    # Semicolon
                ", ",    # Comma
                " ",     # Space
                ""       # Character level
            ]
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
            is_separator_regex=False
        )
    
    def process_documents(self, documents: List[Document]) -> List[Document]:
        """
        Process documents into chunks
        
        Args:
            documents: List of LangChain Document objects
            
        Returns:
            List of chunked Document objects
        """
        print(f"Processing {len(documents)} documents into chunks...")
        
        chunked_documents = []
        
        for i, doc in enumerate(documents):
            try:
                # Split the document
                chunks = self.text_splitter.split_documents([doc])
                
                # Add chunk-specific metadata
                for j, chunk in enumerate(chunks):
                    # Update metadata with chunk information
                    chunk.metadata.update({
                        'chunk_index': j,
                        'total_chunks': len(chunks),
                        'chunk_id': f"{doc.metadata.get('id', 'unknown')}_chunk_{j}",
                        'parent_doc_id': doc.metadata.get('id', 'unknown'),
                        'chunk_size': len(chunk.page_content),
                        'original_length': len(doc.page_content)
                    })
                    
                    chunked_documents.append(chunk)
                
                if (i + 1) % 100 == 0:
                    print(f"Processed {i + 1}/{len(documents)} documents...")
                    
            except Exception as e:
                print(f"Error processing document {doc.metadata.get('id', 'unknown')}: {str(e)}")
                continue
        
        print(f"Created {len(chunked_documents)} chunks from {len(documents)} documents")
        return chunked_documents
    
    def get_chunk_statistics(self, chunks: List[Document]) -> Dict[str, Any]:
        """
        Get statistics about the chunks
        
        Args:
            chunks: List of chunked documents
            
        Returns:
            Dictionary with statistics
        """
        if not chunks:
            return {"error": "No chunks provided"}
        
        chunk_sizes = [len(chunk.page_content) for chunk in chunks]
        
        # Count chunks by source
        source_counts = {}
        category_counts = {}
        
        for chunk in chunks:
            source = chunk.metadata.get('source', 'unknown')
            category = chunk.metadata.get('category', 'unknown')
            
            source_counts[source] = source_counts.get(source, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1
        
        stats = {
            'total_chunks': len(chunks),
            'avg_chunk_size': sum(chunk_sizes) / len(chunk_sizes),
            'min_chunk_size': min(chunk_sizes),
            'max_chunk_size': max(chunk_sizes),
            'chunks_by_source': source_counts,
            'chunks_by_category': category_counts,
            'total_characters': sum(chunk_sizes)
        }
        
        return stats
    
    def save_chunks(self, chunks: List[Document], output_path: str = "processed_data/chunks.json"):
        """
        Save chunks to JSON file for inspection
        
        Args:
            chunks: List of chunked documents
            output_path: Path to save the chunks
        """
        import json
        import os
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        chunks_data = []
        for chunk in chunks:
            chunk_data = {
                'content': chunk.page_content,
                'metadata': chunk.metadata
            }
            chunks_data.append(chunk_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(chunks)} chunks to {output_path}")


def process_training_data(input_file: str = "processed_data/training_data.json",
                         chunk_size: int = 1000,
                         chunk_overlap: int = 200) -> List[Document]:
    """
    Complete pipeline to load and chunk training data
    
    Args:
        input_file: Path to training data JSON file
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of chunked documents
    """
    # Load documents
    documents = load_training_data(input_file)
    
    # Initialize processor
    processor = DocumentChunkProcessor(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    # Process into chunks
    chunks = processor.process_documents(documents)
    
    # Get and print statistics
    stats = processor.get_chunk_statistics(chunks)
    print("\nChunking Statistics:")
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Average chunk size: {stats['avg_chunk_size']:.1f} characters")
    print(f"Min chunk size: {stats['min_chunk_size']}")
    print(f"Max chunk size: {stats['max_chunk_size']}")
    print(f"Total characters: {stats['total_characters']}")
    
    # Save chunks for inspection
    processor.save_chunks(chunks)
    
    return chunks


if __name__ == "__main__":
    # Test the chunking processor
    try:
        chunks = process_training_data()
        print(f"\nSuccessfully created {len(chunks)} chunks")
        
        # Show example chunk
        if chunks:
            example_chunk = chunks[0]
            print("\nExample chunk:")
            print(f"Chunk ID: {example_chunk.metadata.get('chunk_id')}")
            print(f"Parent Doc ID: {example_chunk.metadata.get('parent_doc_id')}")
            print(f"Chunk {example_chunk.metadata.get('chunk_index') + 1} of {example_chunk.metadata.get('total_chunks')}")
            print(f"Size: {example_chunk.metadata.get('chunk_size')} characters")
            print(f"Content: {example_chunk.page_content[:300]}...")
            
    except Exception as e:
        print(f"Error: {str(e)}")