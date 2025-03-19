from typing import List, Dict, Any
import pandas as pd
import numpy as np 
import os
from loguru import logger
import PyPDF2


class FileProcessor:
    """Base class for file processing"""

    def __init__(self):
        self.supported_extensions = ['.csv', '.xlsx', '.xls', '.txt', '.doc', '.docx', '.pdf', '.json']

    def process_file(self, file_path: str):
        """Process a  file with its respective extension"""
        extension = os.path.splitext(file_path)[1]
        if extension not in self.supported_extensions:
            raise ValueError(f"Unsupported file extension: {extension}")
        
        if extension == '.csv':
            return self._process_csv(file_path)
        elif extension == '.xlsx' or extension == '.xls':
            return self._process_excel(file_path)
        elif extension == '.txt':
            return self._process_txt(file_path)
        elif extension == '.doc' or extension == '.docx':
            return self._process_doc(file_path)
        elif extension == '.pdf':
            return self._process_pdf(file_path)
        elif extension == '.json':
            return self._process_json(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {extension}")
            
    def _process_csv(self, file_path: str) -> Dict[str, Any]:
        """Process a CSV file and return a dictionary"""
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Successfully processed CSV file from path: {file_path}")
            return {
                'data': df,
                'metadata': {
                    'rows': df.shape[0],
                    'columns': df.shape[1],
                    'dtypes': {col: dtype for col, dtype in df.dtypes.items()},
                    'summary': self._get_summary(df)
                },
                
            }
        except Exception as e:
            logger.error(f"Error processing CSV file from path: {file_path}. Error: {e}")
            raise e
        
    def _process_excel(self, file_path: str) -> Dict[str, Any]:
        """Process an Excel file and return a dictionary"""
        try:
            excel_file = pd.ExcelFile(file_path)
            sheets = {}

            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                sheets[sheet_name] = {
                    'data': df, 
                    'metadata': {
                        'rows': df.shape[0],
                        'columns': df.shape[1],
                        'dtypes': {col: dtype for col, dtype in df.dtypes.items()},
                        'summary': self._get_summary(df)
                    },
                    
                }
            
            return {
                'sheets': sheets,
                'sheet_names': excel_file.sheet_names
            }
        except Exception as e:
            logger.error(f"Error processing Excel file from path: {file_path}. Error: {e}")
            raise e
                
        
    def _process_txt(self, file_path: str) -> Dict[str, Any]:
        """Process a text file and return a dictionary"""
        try:
            df = pd.read_csv(file_path, sep='\t')
            logger.info(f"Successfully processed text file from path: {file_path}")
            return {
                'data': df,
                'metadata': {
                    'rows': df.shape[0],
                    'columns': df.shape[1],
                    'dtypes': {col: dtype for col, dtype in df.dtypes.items()},
                    'summary': self._get_summary(df)
                },
                
            }
        except Exception as e:
            logger.error(f"Error processing text file from path: {file_path}. Error: {e}")
            raise e
        
    def _process_json(self, file_path: str) -> Dict[str, Any]:
        """Process a JSON file and return a dictionary"""
        try:
            df = pd.read_json(file_path)
            logger.info(f"Successfully processed JSON file from path: {file_path}")
            return {
                'data': df,
                'metadata': {
                    'rows': df.shape[0],
                    'columns': df.shape[1],
                    'dtypes': {col: dtype for col, dtype in df.dtypes.items()},
                    'summary': self._get_summary(df)
                },
                
            }
        except Exception as e:
            logger.error(f"Error processing JSON file from path: {file_path}. Error: {e}")
            raise e
        
    def _get_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics of the DataFrame"""
        summary = {}

        summary['numeric_columns'] = df.select_dtypes(include=[np.number]).columns.tolist()
        summary['categorical_columns'] = df.select_dtypes(include=['object', 'bool']).columns.tolist()
        summary['date_columns'] = df.select_dtypes(include=['datetime64']).columns.tolist()

        summary['missing_values'] = df.isnull().sum().to_dict()
        summary['duplicates'] = df.duplicated().sum()

        try:
            summary['basic_stats'] = df.describe().to_dict()
        except Exception as e:
            logger.error(f"Error getting basic stats: {e}")
            summary['basic_stats'] = {}

        return summary
    

# Example usage
if __name__ == "__main__":
    processor = FileProcessor()
    file_path = 'data/sample.csv'
    result = processor.process_file(file_path)
    print(result['metadata'])