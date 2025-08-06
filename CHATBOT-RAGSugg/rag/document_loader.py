"""
Document Loader for RAG System
Loads JSON documents using LangChain
"""

import json
import os
from typing import List, Dict, Any
from langchain.docstore.document import Document



class JSONDocumentLoader():
    """
    Custom LangChain loader for our JSON training data
    """
    
    def __init__(self, file_path: str):
        """
        Initialize the JSON loader
        
        Args:
            file_path: Path to the JSON file
        """
        self.file_path = file_path
        
    def load(self) -> List[Document]:
        """
        Load documents from JSON file
        
        Returns:
            List of LangChain Document objects
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = []
            
            for item in data:
                # Extract text content
                text_content = item.get('text', '')
                
                if not text_content:
                    print(f"Warning: Empty text content for document ID: {item.get('id', 'unknown')}")
                    continue
                
                # Create metadata
                metadata = {
                    'id': item.get('id', 'unknown'),
                    'source': item.get('metadata', {}).get('source', 'unknown'),
                    'category': item.get('metadata', {}).get('category', 'unknown'),
                    'length': item.get('metadata', {}).get('length', len(text_content)),
                    'file_path': self.file_path
                }
                
                # Add any additional metadata
                if 'metadata' in item:
                    for key, value in item['metadata'].items():
                        if key not in metadata:
                            metadata[key] = value
                
                # Create LangChain Document
                doc = Document(
                    page_content=text_content,
                    metadata=metadata
                )
                
                documents.append(doc)
            
            print(f"Loaded {len(documents)} documents from {self.file_path}")
            return documents
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in file {self.file_path}: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error loading documents from {self.file_path}: {str(e)}")


def load_training_data(file_path: str = "processed_data/training_data.json") -> List[Document]:
    """
    Convenience function to load training data
    
    Args:
        file_path: Path to training data JSON file
        
    Returns:
        List of LangChain Document objects
    """
    loader = JSONDocumentLoader(file_path)
    return loader.load()


if __name__ == "__main__":
    # Test the loader
    try:
        documents = load_training_data()
        print(f"Successfully loaded {len(documents)} documents")
        
        # Show first document as example
        if documents:
            first_doc = documents[0]
            print("\nFirst document preview:")
            print(f"ID: {first_doc.metadata.get('id')}")
            print(f"Source: {first_doc.metadata.get('source')}")
            print(f"Category: {first_doc.metadata.get('category')}")
            print(f"Content length: {len(first_doc.page_content)}")
            print(f"Content preview: {first_doc.page_content[:200]}...")
            
    except Exception as e:
        print(f"Error: {str(e)}")