# CORRECT IMPORT: BaseTool lives in the main 'crewai' package
from crewai.tools import BaseTool

class ReadFileTool(BaseTool):
    name: str = "Read File"
    description: str = "Reads the content of a file. Input must be the file_path."

    def _run(self, file_path: str) -> str:
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

class WriteFileTool(BaseTool):
    name: str = "Write File"
    description: str = "Writes content to a file. Inputs: file_path and content."

    def _run(self, file_path: str, content: str) -> str:
        try:
            with open(file_path, 'w') as f:
                f.write(content)
            return "File successfully written."
        except Exception as e:
            return f"Error writing file: {e}"