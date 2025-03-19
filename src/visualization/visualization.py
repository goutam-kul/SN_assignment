from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from loguru import logger

class VisualizationEngine:
    """Class for generating visualizations from data"""

    def __init__(self):
        self.default_style = {
            'matplotlib': {
                'figsize': (10, 6),
                'dpi': 100,
                'style': 'seaborn-v0_8'
            },
            'seaborn': {
                'style': 'darkgrid',
                'palette': 'deep'
            },
            'plotly': {
                'template': 'plotly_dark'
            }
        }
    
    def generate_visualization(
        self, 
        df: pd.DataFrame,
        viz_type: str,
        x_column: str = None,
        y_column: str = None,
        category_column: str = None,
        title: str = None,
        engine: str = 'seaborn'
    ) -> Dict[str, Any]:
        """Generate a visualization based on the provided parameters"""
        # if engine == 'matplotlib':
        #     return self._matplotlib_viz(df, viz_type, x_column, y_column, category_column, title)
        if engine == 'seaborn':
            return self._seaborn_viz(df, viz_type, x_column, y_column, category_column, title)
        # elif engine == 'plotly':
        #     return self._plotly_viz(df, viz_type, x_column, y_column, category_column, title)
        else:
            raise ValueError(f"Unsupported visualization engine: {engine}")
        

    def _seaborn_viz(
        self,
        df: pd.DataFrame,
        viz_type: str,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        category_column: Optional[str] = None,
        title: str = "Data Visualization"
    ) -> Dict[str, Any]:
        """Generate a seaborn visualization"""
        
        # Set style
        sns.set_style(self.default_style['seaborn']['style'])
        sns.set_palette(self.default_style['seaborn']['palette'])
        plt.figure(
            figsize=self.default_style['matplotlib']['figsize'],
            dpi=self.default_style['matplotlib']['dpi']
        )

        # Bar Chart
        logger.info(f"Generating seaborn visualization for type: {viz_type}")
        if viz_type == 'bar':
            if category_column:
               ax = sns.barplot(x=x_column, y=y_column, hue=category_column, data=df)
            else:
                ax = sns.barplot(x=x_column, y=y_column, data=df)
        
        # Line Chart
        elif viz_type == 'line':
            if category_column:
                ax = sns.lineplot(x=x_column, y=y_column, hue=category_column, data=df)
            else:
                ax = sns.lineplot(x=x_column, y=y_column, data=df)

        # Scatter Plot
        elif viz_type == 'scatter':
            if category_column:
                ax = sns.scatterplot(x=x_column, y=y_column, hue=category_column, data=df)
            else:
                ax = sns.scatterplot(x=x_column, y=y_column, data=df)

        # Histogram
        elif viz_type == 'histogram':
            ax = sns.histplot(x=df[x_column].dropna(), data=df)

        # Box Plot
        elif viz_type == 'boxplot':
            if category_column:
                ax = sns.boxplot(x=category_column, y=y_column, data=df)
            else:
                ax = sns.boxplot(x=x_column, y=y_column, data=df)

        # Heatmap
        elif viz_type == "heatmap":
            if x_column and y_column and category_column:
                pivot_df = df.pivot_table(index=y_column, columns=x_column, values=category_column)
                ax = sns.heatmap(pivot_df, annot=True, cmap="viridis")
            else:
                corr_df = df.select_dtypes(include=[np.number]).corr()
                ax = sns.heatmap(corr_df, annot=True, cmap="coolwarm")

        # Pie Chart
        elif viz_type == "pie":
            if category_column:
                ax = sns.pieplot(x=category_column, data=df)
            else:
                ax = sns.pieplot(x=x_column, data=df)
                
        else:
            raise ValueError(f"Unsupported visualization type: {viz_type}")
        
        # Set title
        plt.title(title)
        plt.tight_layout()

        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()

        return {
            'figure': image_base64,
            'format': 'base64_png',
            'title': title,
            'type': viz_type,
            'engine': 'seaborn'
        }
    

# Example usage
if __name__ == "__main__":
    engine = VisualizationEngine()
    df = pd.read_csv('data/sample.csv')
    fig = engine.generate_visualization(
        df=df,
        viz_type='line',
        x_column='CreditScore',
        y_column='LoanAmount',
        category_column='AccountType',
        title='Line Chart',
        engine='seaborn'
    )
    image_data = fig['figure']
    image_data = base64.b64decode(image_data)
    with open('output.png', 'wb') as f:
        f.write(image_data)
    print("Visualization saved as output.png")

    