import json
import os
from typing import List, Dict, Any
from datetime import datetime
import uuid

class DatasetProcessor:
    def __init__(self, output_dir: str = "processed_data"):
        """
        Initialize the dataset processor
        
        Args:
            output_dir: Directory to store processed datasets
        """
        self.output_dir = output_dir
        self.unified_data = []
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def normalize_dataset_1(self, data: List[Dict]) -> List[Dict]:
        """
        Normalize Dataset 1 (ChatGPT-4o style conversations)
        Structure: [{"system": "...", "user": "...", "assistant": "..."}]
        """
        normalized = []
        
        for record in data:
            # Create unique ID
            record_id = str(uuid.uuid4())
            
            # Combine user question and assistant response as main content
            user_question = record.get("user", "")
            assistant_response = record.get("assistant", "")
            
            # Create unified content
            content = f"Question: {user_question}\n\nAnswer: {assistant_response}"
            
            unified_record = {
                "id": record_id,
                "content": content,
                "metadata": {
                    "source": "chatgpt_conversations",
                    "category": "financial_qa",
                    "content_type": "conversation",
                    "date": datetime.now().isoformat(),
                    "original_fields": {
                        "system": record.get("system", ""),
                        "user": user_question,
                        "assistant": assistant_response
                    },
                    "content_length": len(content),
                    "has_user_query": bool(user_question),
                    "has_assistant_response": bool(assistant_response)
                }
            }
            
            normalized.append(unified_record)
        
        return normalized
    
    def normalize_dataset_2(self, data: List[Dict]) -> List[Dict]:
        """
        Normalize Dataset 2 (Instruction-based financial data)
        Structure: [{"instruction": "...", "input": "...", "output": "..."}]
        """
        normalized = []
        
        for record in data:
            # Create unique ID
            record_id = str(uuid.uuid4())
            
            # Get fields
            instruction = record.get("instruction", "")
            input_text = record.get("input", "")
            output_text = record.get("output", "")
            
            # Create unified content
            if input_text:
                content = f"Instruction: {instruction}\n\nInput: {input_text}\n\nOutput: {output_text}"
            else:
                content = f"Question: {instruction}\n\nAnswer: {output_text}"
            
            unified_record = {
                "id": record_id,
                "content": content,
                "metadata": {
                    "source": "financial_instructions",
                    "category": "financial_analysis",
                    "content_type": "instruction_response",
                    "date": datetime.now().isoformat(),
                    "original_fields": {
                        "instruction": instruction,
                        "input": input_text,
                        "output": output_text
                    },
                    "content_length": len(content),
                    "has_input": bool(input_text),
                    "instruction_type": self._classify_instruction(instruction)
                }
            }
            
            normalized.append(unified_record)
        
        return normalized
    
    def normalize_dataset_3(self, data: List[Dict]) -> List[Dict]:
        """
        Normalize Dataset 3 (Simple Q&A format)
        Structure: [{"instruction": "...", "input": "...", "output": "...", "text": "..."}]
        """
        normalized = []
        
        for record in data:
            # Create unique ID
            record_id = str(uuid.uuid4())
            
            # Get fields
            instruction = record.get("instruction", "")
            input_text = record.get("input", "")
            output_text = record.get("output", "")
            text_field = record.get("text", "")
            
            # Create unified content - prioritize output over text field
            main_content = output_text if output_text else text_field
            
            if input_text:
                content = f"Question: {instruction}\n\nContext: {input_text}\n\nAnswer: {main_content}"
            else:
                content = f"Question: {instruction}\n\nAnswer: {main_content}"
            
            unified_record = {
                "id": record_id,
                "content": content,
                "metadata": {
                    "source": "simple_qa",
                    "category": "general_financial",
                    "content_type": "question_answer",
                    "date": datetime.now().isoformat(),
                    "original_fields": {
                        "instruction": instruction,
                        "input": input_text,
                        "output": output_text,
                        "text": text_field
                    },
                    "content_length": len(content),
                    "has_input": bool(input_text),
                    "question_type": self._classify_question(instruction)
                }
            }
            
            normalized.append(unified_record)
        
        return normalized
    
    def _classify_instruction(self, instruction: str) -> str:
        """Classify instruction type based on content"""
        instruction_lower = instruction.lower()
        
        if any(word in instruction_lower for word in ['dividend', 'equity', 'wacc', 'cost of capital']):
            return "corporate_finance"
        elif any(word in instruction_lower for word in ['interest', 'rate', 'forecasting', 'expense']):
            return "financial_analysis"
        elif any(word in instruction_lower for word in ['investment', 'portfolio', 'risk']):
            return "investment_advice"
        else:
            return "general_finance"
    
    def _classify_question(self, question: str) -> str:
        """Classify question type based on content"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['scam', 'financing', 'rebate', 'car']):
            return "consumer_finance"
        elif any(word in question_lower for word in ['central bank', 'interest rate', 'monetary policy']):
            return "monetary_policy"
        elif any(word in question_lower for word in ['invest', 'investment', 'money']):
            return "investment_advice"
        else:
            return "general_finance"
    
    def process_json_file(self, file_path: str, dataset_type: int) -> List[Dict]:
        """
        Process a JSON file based on its dataset type
        
        Args:
            file_path: Path to the JSON file
            dataset_type: Type of dataset (1, 2, or 3)
        
        Returns:
            List of normalized records
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if dataset_type == 1:
            return self.normalize_dataset_1(data)
        elif dataset_type == 2:
            return self.normalize_dataset_2(data)
        elif dataset_type == 3:
            return self.normalize_dataset_3(data)
        else:
            raise ValueError(f"Invalid dataset type: {dataset_type}")
    
    def process_all_datasets(self, file_paths: List[str], dataset_types: List[int]) -> None:
        """
        Process multiple datasets and combine them
        
        Args:
            file_paths: List of paths to JSON files
            dataset_types: List of dataset types corresponding to each file
        """
        if len(file_paths) != len(dataset_types):
            raise ValueError("Number of file paths must match number of dataset types")
        
        all_normalized_data = []
        
        for file_path, dataset_type in zip(file_paths, dataset_types):
            print(f"Processing {file_path} as dataset type {dataset_type}...")
            
            try:
                normalized_data = self.process_json_file(file_path, dataset_type)
                all_normalized_data.extend(normalized_data)
                print(f"Successfully processed {len(normalized_data)} records from {file_path}")
            
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                continue
        
        self.unified_data = all_normalized_data
        print(f"\nTotal unified records: {len(self.unified_data)}")
    
    def save_unified_dataset(self, filename: str = "unified_dataset.json") -> str:
        """
        Save the unified dataset to a JSON file
        
        Args:
            filename: Name of the output file
        
        Returns:
            Path to the saved file
        """
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.unified_data, f, indent=2, ensure_ascii=False)
        
        print(f"Unified dataset saved to: {output_path}")
        return output_path
    
    def save_by_source(self) -> Dict[str, str]:
        """
        Save datasets separated by source
        
        Returns:
            Dictionary mapping source names to file paths
        """
        sources = {}
        
        # Group by source
        for record in self.unified_data:
            source = record['metadata']['source']
            if source not in sources:
                sources[source] = []
            sources[source].append(record)
        
        # Save each source separately
        file_paths = {}
        for source, records in sources.items():
            filename = f"{source}_dataset.json"
            output_path = os.path.join(self.output_dir, filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
            
            file_paths[source] = output_path
            print(f"Saved {len(records)} records to: {output_path}")
        
        return file_paths
    
    def get_dataset_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the unified dataset
        
        Returns:
            Dictionary with dataset statistics
        """
        if not self.unified_data:
            return {"error": "No data processed yet"}
        
        # Basic stats
        total_records = len(self.unified_data)
        
        # Source distribution
        source_counts = {}
        category_counts = {}
        content_type_counts = {}
        
        total_content_length = 0
        
        for record in self.unified_data:
            metadata = record['metadata']
            
            # Count by source
            source = metadata['source']
            source_counts[source] = source_counts.get(source, 0) + 1
            
            # Count by category
            category = metadata['category']
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # Count by content type
            content_type = metadata['content_type']
            content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
            
            # Content length
            total_content_length += metadata['content_length']
        
        avg_content_length = total_content_length / total_records
        
        return {
            "total_records": total_records,
            "average_content_length": avg_content_length,
            "source_distribution": source_counts,
            "category_distribution": category_counts,
            "content_type_distribution": content_type_counts
        }
    
    def prepare_for_training(self, output_file: str = "training_data.json") -> str:
        """
        Prepare data specifically for RAG training
        
        Args:
            output_file: Name of the training data file
        
        Returns:
            Path to the training data file
        """
        training_data = []
        
        for record in self.unified_data:
            # Create training format
            training_record = {
                "id": record["id"],
                "text": record["content"],
                "metadata": {
                    "source": record["metadata"]["source"],
                    "category": record["metadata"]["category"],
                    "length": record["metadata"]["content_length"]
                }
            }
            
            training_data.append(training_record)
        
        # Save training data
        training_path = os.path.join(self.output_dir, output_file)
        with open(training_path, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)
        
        print(f"Training data saved to: {training_path}")
        return training_path


