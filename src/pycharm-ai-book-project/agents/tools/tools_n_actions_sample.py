from typing import Dict, Any, Callable
from abc import ABC, abstractmethod

class Tool(ABC):

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _get_parameters(self) -> Dict[str, Any]:
        """Return parameter schema for this tool"""
        pass

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self._get_parameters()
        }


class CalculatorTool(Tool):

    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform mathematical calculations"
        )

    def run(self, expression: str) -> Dict[str, Any]:
        try:
            # Safely evaluate mathematical expression
            # Note: In production, use a proper math parser like sympy
            allowed_names = {
                "abs": abs, "round": round, "pow": pow,
                "max": max, "min": min, "sum": sum
            }
            result = eval(expression, {"__builtins__": {}}, allowed_names)

            return {"success": True, "result": result}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
        
    def _get_parameters(self):
        return {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to evaluate"
            }
        }