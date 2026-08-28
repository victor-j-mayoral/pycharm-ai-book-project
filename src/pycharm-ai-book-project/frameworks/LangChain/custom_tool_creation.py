from langchain.tools import BaseTool
from typing import Optional, Type
from pydantic import BaseModel, Field
import pandas as pd


 # Define tool input schema
class DataAnalysisInput(BaseModel):
    query: str = Field(description="SQL query to analyze data")
    visualization: Optional[str] = Field(
        default=None,
        description="Type of visualization (bar, line, scatter)"
    )


class DataAnalysisTool(BaseTool):
    name: str = "data_analyzer"
    description: str = "Analyze data using SQL queries and create visualizations"
    args_schema: Type[BaseModel] = DataAnalysisInput

    def __init__(self, database_url: str):
        super().__init__()
        self.database_url = database_url

    def _run(self, query: str, visualization: Optional[str] = None) -> str:
        try:
            # Execute query
            df = pd.read_sql(query, self.database_url)
            # Generate analysis
            analysis = self._analyze_dataframe(df)
             # Create visualization if requested
            if visualization:
                viz_path = self._create_visualization(df, visualization)
                analysis += f"\nVisualization saved to: {viz_path}"

            return analysis
        
        except Exception as e:

            return f"Analysis failed: {str(e)}"
        
    async def _arun(self, query: str, visualization: Optional[str] = None) -> str:

        # Async implementation
        return self._run(query, visualization)

    def _analyze_dataframe(self, df: pd.DataFrame) -> str:
        analysis = f"Data shape: {df.shape}\n"
        analysis += f"Columns: {', '.join(df.columns)}\n"
        analysis += f"\nSummary statistics:\n{df.describe()}\n"
         # Add insights
        if len(df) > 0:
            analysis += f"\nKey insights:\n"
            for col in df.select_dtypes(include=['number']).columns:
                analysis += f"- {col}: mean={df[col].mean():.2f}, std={df[col].std():.2f}\n"

        return analysis