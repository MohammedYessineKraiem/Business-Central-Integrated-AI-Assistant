"""
Simple script to process your 3 JSON datasets
Run this from your rag/ directory
"""

from data_processing import DatasetProcessor
import os

def main():
    print("Starting dataset processing...")
    
    # First, let's check what files actually exist in raw_data/
    raw_data_dir = "raw_data"
    
    if not os.path.exists(raw_data_dir):
        print(f"Error: {raw_data_dir} directory not found!")
        print("Please make sure you're running this script from the rag/ directory")
        return
    
    # List all files in raw_data/
    print(f"\nFiles found in {raw_data_dir}/:")
    files_in_dir = os.listdir(raw_data_dir)
    json_files = [f for f in files_in_dir if f.endswith('.json')]
    
    for file in files_in_dir:
        print(f"  - {file}")
    
    if not json_files:
        print("No JSON files found in raw_data/ directory!")
        return
    
    print(f"\nJSON files found: {json_files}")
    
    # Initialize processor
    processor = DatasetProcessor(output_dir="processed_data")
    
    # Define your dataset files and their types
    # Update these paths based on your actual file names
    file_paths = []
    dataset_types = []
    
    # Look for your dataset files (adjust names if needed)
    expected_files = [
        ("dataset1.json", 1),  # ChatGPT-4o conversations
        ("dataset2.json", 2),  # Instruction-based financial data
        ("dataset3.json", 3)   # Simple Q&A format
    ]
    
    for filename, dataset_type in expected_files:
        file_path = os.path.join(raw_data_dir, filename)
        if os.path.exists(file_path):
            file_paths.append(file_path)
            dataset_types.append(dataset_type)
            print(f" Found: {filename}")
        else:
            print(f" Missing: {filename}")
    
    if not file_paths:
        print("\nNo dataset files found! Please check your file names.")
        print("Expected files: dataset1.json, dataset2.json, dataset3.json")
        return
    
    # Check current working directory
    print(f"\nCurrent working directory: {os.getcwd()}")
    
    try:
        # Process all datasets
        processor.process_all_datasets(file_paths, dataset_types)
        
        # Save unified dataset
        unified_path = processor.save_unified_dataset()
        
        # Save by source (optional)
        source_paths = processor.save_by_source()
        
        # Get statistics
        stats = processor.get_dataset_stats()
        print("\n" + "="*50)
        print("DATASET STATISTICS")
        print("="*50)
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        # Prepare for training
        training_path = processor.prepare_for_training()
        
        print("\n" + "="*50)
        print("FILES CREATED")
        print("="*50)
        print(f" Unified dataset: {unified_path}")
        print(f" Training data: {training_path}")
        print(" Source-separated files:")
        for source, path in source_paths.items():
            print(f"  - {source}: {path}")
        
        print("\n" + "="*50)
        print("SUCCESS! Your datasets are ready for RAG training")
        print("="*50)
        print(f"Use this file for chunking and embeddings: {training_path}")
        
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        print("Please check your JSON files and try again")

if __name__ == "__main__":
    main()