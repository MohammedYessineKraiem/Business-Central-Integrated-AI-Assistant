"""
Vector Store Manager for RAG System
Handles ChromaDB vector storage and embeddings
"""

import os
import json
import shutil
from typing import List, Optional, Dict, Any
from langchain.docstore.document import Document
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from chunking_processor import process_training_data


class VectorStoreManager:
    """
    Manages ChromaDB vector store for RAG system
    """

    def __init__(self, 
                 collection_name: str = "financial_qa_collection",
                 persist_directory: str = "chroma_db",
                 embedding_model: str = "all-MiniLM-L6-v2"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embedding_model_name = embedding_model

        print(f"Loading embedding model: {embedding_model}")
        self.embeddings = SentenceTransformerEmbeddings(model_name=embedding_model)
        self.vectorstore = None

    def create_vectorstore(self, documents: List[Document]) -> Chroma:
        """
        Create a new vector store from documents
        """
        print(f"Creating new vector store with {len(documents)} documents...")

        # Assume caller manages deleting old data if needed — do NOT delete here.

        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=self.collection_name,
            persist_directory=self.persist_directory
        )
        self.vectorstore.persist()

        metadata_path = os.path.join(self.persist_directory, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump({"status": "complete"}, f)

        print(f"Vector store created and persisted to {self.persist_directory}")
        return self.vectorstore


    def load_vectorstore(self) -> Optional[Chroma]:
        """
        Load existing vector store if valid
        """
        if not os.path.exists(self.persist_directory):
            print(f"No vector store found at {self.persist_directory}")
            return None

        # Check for metadata marker
        metadata_path = os.path.join(self.persist_directory, "metadata.json")
        if not os.path.exists(metadata_path):
            print("Metadata file not found. Vector store may be incomplete.")
            return None

        try:
            print(f"Loading vector store from {self.persist_directory}")
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
            count = self.vectorstore._collection.count()
            if count == 0:
                print("Vector store is empty.")
                return None

            print(f"Loaded vector store with {count} documents")
            return self.vectorstore

        except Exception as e:
            print(f"Error loading vector store: {str(e)}")
            return None

    def add_documents(self, documents: List[Document]) -> None:
        if not self.vectorstore:
            print("No vector store loaded. Creating new one...")
            self.create_vectorstore(documents)
            return

        print(f"Adding {len(documents)} documents to existing vector store...")
        self.vectorstore.add_documents(documents)
        self.vectorstore.persist()
        print(f"Successfully added {len(documents)} documents")

    def similarity_search(self, query: str, k: int = 5,
                          filter_dict: Optional[Dict[str, Any]] = None) -> List[Document]:
        if not self.vectorstore:
            raise ValueError("Vector store not loaded.")
        print(f"Searching for: '{query}' (top {k} results)")
        if filter_dict:
            return self.vectorstore.similarity_search(query=query, k=k, filter=filter_dict)
        return self.vectorstore.similarity_search(query=query, k=k)

    def similarity_search_with_score(self, query: str, k: int = 5,
                                     filter_dict: Optional[Dict[str, Any]] = None) -> List[tuple]:
        if not self.vectorstore:
            raise ValueError("Vector store not loaded.")
        print(f"Searching with scores for: '{query}' (top {k} results)")
        if filter_dict:
            return self.vectorstore.similarity_search_with_score(query=query, k=k, filter=filter_dict)
        return self.vectorstore.similarity_search_with_score(query=query, k=k)

    def get_collection_stats(self) -> Dict[str, Any]:
        if not self.vectorstore:
            return {"error": "Vector store not loaded"}

        try:
            collection = self.vectorstore._collection
            count = collection.count()
            sample_docs = self.vectorstore.similarity_search("sample", k=min(10, count))
            sources = set()
            categories = set()

            for doc in sample_docs:
                sources.add(doc.metadata.get('source', 'unknown'))
                categories.add(doc.metadata.get('category', 'unknown'))

            return {
                'total_documents': count,
                'collection_name': self.collection_name,
                'embedding_model': self.embedding_model_name,
                'persist_directory': self.persist_directory,
                'sources': list(sources),
                'categories': list(categories)
            }

        except Exception as e:
            return {"error": f"Error getting stats: {str(e)}"}

    def delete_collection(self) -> None:
        # Clean up active connection first
        if self.vectorstore:
            try:
                self.vectorstore._client.reset()
                self.vectorstore = None
            except Exception as e:
                print(f"Warning: Failed to reset Chroma client cleanly: {e}")

        # Remove from disk
        if os.path.exists(self.persist_directory):
            try:
                shutil.rmtree(self.persist_directory)
                print(f"Deleted vector store at {self.persist_directory}")
            except Exception as e:
                print(f"Error deleting vector store: {e}")
        else:
            print("No vector store to delete")


def create_vector_database(input_file: str = "processed_data/training_data.json",
                           chunk_size: int = 1000,
                           chunk_overlap: int = 200,
                           force_recreate: bool = False) -> VectorStoreManager:
    """
    Initializes the full vector store system
    """
    manager = VectorStoreManager()

    if not force_recreate:
        existing_store = manager.load_vectorstore()
        if existing_store:
            print("Using existing vector store")
            return manager
        elif os.path.exists(manager.persist_directory):
            raise RuntimeError(
                "Vector store directory exists but failed to load or is incomplete. "
                "Use force_recreate=True to rebuild."
            )

    print("Processing training data into chunks...")
    chunks = process_training_data(
        input_file=input_file,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    print("Creating vector embeddings...")
    manager.create_vectorstore(chunks)

    stats = manager.get_collection_stats()
    print("\nVector Store Statistics:")
    print(f"Total documents: {stats.get('total_documents', 'unknown')}")
    print(f"Collection name: {stats.get('collection_name', 'unknown')}")
    print(f"Embedding model: {stats.get('embedding_model', 'unknown')}")
    print(f"Sources: {stats.get('sources', [])}")
    print(f"Categories: {stats.get('categories', [])}")

    return manager


if __name__ == "__main__":
    try:
        manager = create_vector_database(force_recreate=False)

        print("\nTesting similarity search...")
        query = "What are the tax implications of self-employment?"
        results = manager.similarity_search(query, k=3)

        print(f"\nSearch results for: '{query}'")
        for i, doc in enumerate(results):
            print(f"\nResult {i+1}:")
            print(f"Source: {doc.metadata.get('source', 'unknown')}")
            print(f"Category: {doc.metadata.get('category', 'unknown')}")
            print(f"Chunk ID: {doc.metadata.get('chunk_id', 'unknown')}")
            print(f"Content: {doc.page_content[:200]}...")

        print("\nTesting similarity search with scores...")
        scored_results = manager.similarity_search_with_score(query, k=3)
        for i, (doc, score) in enumerate(scored_results):
            print(f"\nResult {i+1} (Score: {score:.4f}):")
            print(f"Content: {doc.page_content[:150]}...")

    except Exception as e:
        print(f"Error: {str(e)}")
