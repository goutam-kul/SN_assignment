from typing import Dict, Any, List
import os 
import json
from src.file_processing.process_file import FileProcessor
from src.llm_handler.data_analysis import DataAnalysisEngine
from src.visualization.visualization import VisualizationEngine
from src.config.settings import settings
from loguru import logger

class DataAnalysisAgent:
    def __init__(self, upload_dir: str = './uploads'):
        self.file_processor = FileProcessor()
        self.data_analysis_engine = DataAnalysisEngine()
        self.visualization_engine = VisualizationEngine()
        self.upload_dir = upload_dir
        self.conversation_history = []
        self.files = {}

    def process_file(self, file_path: str, file_id: str) -> Dict[str, Any]:
        """Process the uploaded file and return the processed data"""
        if not file_id:
            file_id = os.path.basename(file_path)

        # Process the file
        logger.info(f"Processing file: {file_path}")
        processed_data = self.file_processor.process_file(file_path=file_path)
        self.data_analysis_engine.add_data(processed_data, file_id)
        logger.info(f"File processed and data added for file: {file_id}")

        return processed_data
    
    def ask(self, query: str) -> Dict[str, Any]:
        """Ask a question about the data"""
        # Add query to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": query
        })

        # Get default file_id (first file if available)
        file_id = list(self.files.keys())[0] if self.files else None
        if not file_id:
            raise ValueError("No files have been processed yet")

        # Check if query is a visualization request
        viz_keywords = ["plot", "chart", "graph", "visualize", "visualization",
                        "histogram", "line", "bar", "pie", "scatter", "boxplot"]
        viz_request = any(keyword in query.lower() for keyword in viz_keywords)

        if viz_request:
            # Use LLM to parse visualization request
            viz_params = self._parse_visualization_request(query)

            # Get the DataFrame to use for visualization
            viz_file_id = viz_params.get('file_id', file_id)

            if viz_file_id and viz_file_id in self.data_analysis_engine.data_frames:
                df = self.data_analysis_engine.data_frames[viz_file_id]

                # Generate visualization
                viz_result = self.visualization_engine.generate_visualization(
                    df=df,
                    viz_type=viz_params.get('type', 'bar'),
                    x_column=viz_params.get('x_column'),
                    y_column=viz_params.get('y_column'),
                    category_column=viz_params.get('category_column'),
                    title=viz_params.get('title'),
                    engine='seaborn'
                )
                print(viz_result)
                # Add visualization to response
                response = {
                    'type': 'visualization',
                    'data': viz_result,
                    'message': f"Here is the {viz_params['type']} visualization you requested"
                }
            else:
                response = {
                    'type': 'text',
                    'message': f"File {viz_file_id} not found or no data available for visualization"
                }
        else:
            # Perform data analysis
            response = self.data_analysis_engine.analyze_data(
                file_ids=[file_id],
                query=query
            )

            response = {
                'type': 'text',
                'message': response
            }

        # Add response to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": response['message']
        })      

        return response

    def _parse_visualization_request(self, query: str) -> Dict[str, Any]:
        """Parse the visualization request details from the query"""
        prompt = f"""You are a visualization parameter extractor. Your task is to extract visualization parameters from the user's query and return them in a specific JSON format.

        User Query: {query}

        Available files: {list(self.files.keys())}

        IMPORTANT: You must respond with ONLY a valid JSON object, no other text. The JSON must contain these fields:
        - "type": string (one of: "bar", "line", "scatter", "pie", "histogram", "heatmap", "boxplot")
        - "x_column": string
        - "y_column": string or null
        - "category_column": string or null
        - "title": string
        - "file_id": string

        Example Query: "Create a bar chart showing sales by category with title 'Sales Distribution'"
        Example Response:
        {{
            "type": "bar",
            "x_column": "category",
            "y_column": "sales",
            "category_column": null,
            "title": "Sales Distribution",
            "file_id": "data/sample.csv"
        }}
        """

        try:
            logger.info(f"Parsing visualization request: {query}")
            response = self.data_analysis_engine.llm.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Clean the response text to ensure it's valid JSON
            # Remove any potential markdown formatting or extra text
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            logger.info(f"Parsed response: {response_text}")
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Error parsing visualization request: {str(e)}")
            # Return default visualization parameters based on the query
            default_params = {
                'type': 'histogram' if 'histogram' in query.lower() else 'bar',
                'x_column': None,
                'y_column': None,
                'category_column': None,
                'title': None,
                'file_id': list(self.files.keys())[0] if self.files else None
            }
            
            # Try to extract some basic parameters from the query
            if 'x-axis' in query.lower():
                x_start = query.lower().find('x-axis') + 7
                x_end = query.find('.', x_start)
                if x_end == -1:
                    x_end = len(query)
                x_column = query[x_start:x_end].strip()
                default_params['x_column'] = x_column
            
            if 'title' in query.lower():
                title_start = query.lower().find('title') + 5
                title_end = query.find('.', title_start)
                if title_end == -1:
                    title_end = len(query)
                title = query[title_start:title_end].strip(' "\'')
                default_params['title'] = title
            
            return default_params
        
        

# Example usage
if __name__ == "__main__":
    agent = DataAnalysisAgent()
    file_path = 'data/sample.csv'
    processed_data = agent.process_file(file_path=file_path, file_id=file_path)
    agent.files[file_path] = processed_data
    while True:
        query = input("Enter a query: ")
        if query == 'q':
            break
        response = agent.ask(query=query)
        if response['type'] == 'visualization':
            with open('output.png', 'wb') as f:
                f.write(response['data'])
            print("Visualization saved as output.png")
        else:
            print(response['message'])





    
    