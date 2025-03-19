from typing import Dict, Any, List, Optional
from src.visualization.visualization import VisualizationEngine
from src.file_processing.process_file import FileProcessor
from langchain_ollama import ChatOllama
from src.config.settings import settings
from loguru import logger

class DataAnalysisEngine:
    def __init__(self):
        self.llm = ChatOllama(model=settings.llm_model, ollama_url=settings.ollama_url)
        self.file_processor = FileProcessor()
        self.visualization_engine = VisualizationEngine()
        self.context = {}
        self.data_frames = {}

    def add_data(self, processed_file_data: Dict[str, Any], file_id: str):
        """Add processed data to the context"""
        logger.info(f"Adding data for file: {file_id}")
        self.context[file_id] = processed_file_data

        # If DataFrame is available store it for direct analysis
        if 'data' in processed_file_data:
            self.data_frames[file_id] = processed_file_data['data']
        elif 'sheets' in processed_file_data:
            for sheet_name, sheet_data in processed_file_data['sheets'].items():
                self.data_frames[f"{file_id}_{sheet_name}"] = sheet_data['data']
        logger.info(f"Data added for file: {file_id}")

    def analyze_data(self,  file_ids: List[str], query: str):
        """Analyze the data based on the query"""
        if not file_ids:
            file_ids = list(self.context.keys())
        logger.info(f"Analyzing data for files: {file_ids}")
        
        # Prepare context for the LLM
        context_text = self._prepare_context(file_ids)
        logger.info(f"Context prepared for files: {file_ids}")

        # Prepare the prompt
        prompt = f"""
        You are a professional data analyst, analyze the following data and answer the question based on the context provided.

        Context: {context_text}

        Question: {query}

        Instructions:
        - Use the context to answer the question
        - Provide a concise analysis addressing the question directly
        - Enclude all the relevant statistics, calculations, and insights
        - If data is insufficient to answer the question, list the information that is needed
        """

        # Generate the response
        response = self.llm.invoke(prompt)
        logger.info(f"Response generated for files: {file_ids}")
        return response.content if hasattr(response, 'content') else str(response)
    
    def _prepare_context(self, file_ids: List[str]) -> str:
        """Prepare the context for the LLM"""
        context_parts = []

        for file_id in file_ids:
            if file_id not in self.context:
                continue

            data = self.context[file_id]

            if 'data' in data:
                # CSV, JSON or similar format
                context_parts.append(f"File: {file_id}")
                context_parts.append(f"Shape: {data['metadata']['rows']}x{data['metadata']['columns']}")
                columns = [col for col in data['metadata']['dtypes'].keys()]
                context_parts.append(f"Columns: {', '.join(columns)}")
                dtypes_str = ', '.join([f"{col}: {data['metadata']['dtypes'][col]}" for col in columns])
                context_parts.append(f"Data types: {dtypes_str}")
                context_parts.append(f"Summary: {data['metadata']['summary']}")
                context_parts.append("-" * 40)
            elif 'sheets' in data:
                # Excel format
                for sheet_name, sheet_data in data['sheets'].items():
                    context_parts.append(f"Sheet: {sheet_name}")
                    context_parts.append(f"Shape: {sheet_data['metadata']['rows']}x{sheet_data['metadata']['columns']}")
                    columns = [col for col in sheet_data['metadata']['dtypes'].keys()]
                    context_parts.append(f"Columns: {', '.join(columns)}")
                    dtypes_str = ', '.join([f"{col}: {sheet_data['metadata']['dtypes'][col]}" for col in columns])
                    context_parts.append(f"Data types: {dtypes_str}")
                    context_parts.append(f"Summary: {sheet_data['metadata']['summary']}")
                    context_parts.append("-" * 40)

        return "\n".join(context_parts)
                
                


# Example usage
if __name__ == "__main__":
    from src.file_processing.process_file import FileProcessor
    from src.visualization.visualization import VisualizationEngine
    from src.config.settings import settings

    # Initialize components
    file_processor = FileProcessor()
    visualization_engine = VisualizationEngine()
    data_analysis_engine = DataAnalysisEngine()

    # Process a sample file
    file_path = 'data/sample.csv'
    processed_data = file_processor.process_file(file_path=file_path)
    data_analysis_engine.add_data(processed_data, file_id=file_path)

    # Analyze the data
    query = "What is the average loan amount?"
    response = data_analysis_engine.analyze_data(file_ids=[file_path], query=query)
    print(response)
    

