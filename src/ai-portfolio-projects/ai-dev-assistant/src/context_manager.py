# src/context_manager.py

from typing import List, Dict
from pathlib import Path


class ContextManager:

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.file_cache = {}


    def get_related_files(self, current_file: str, max_files: int = 5) -> List[Dict]:

        """Find files related to the current file"""
        current_path = Path(current_file)
        related = []
         # Look for imports in the current file
        try:
            with open(current_file, 'r') as f:
                content = f.read()

            # Simple import detection
            import_lines = [line for line in content.split('\n') 
                          if line.strip().startswith(('import ', 'from '))]
            
            for line in import_lines:
                # Extract module names
                if 'import' in line:
                    parts = line.split()
                    if 'from' in parts:
                        module = parts[parts.index('from') + 1]
                    else:
                        module = parts[parts.index('import') + 1]
                     # Try to find the file
                    possible_path = self.workspace_root / f"{module.replace('.', '/')}.py"
                    if possible_path.exists():
                        related.append({
                            "path": str(possible_path),
                            "relevance": "import"
                        })
        except Exception as e:
            print(f"Error analyzing imports: {e}")
        
        # Look for files in the same directory
        for file in current_path.parent.glob("*.py"):
            if file != current_path and len(related) < max_files:
                related.append({
                    "path": str(file),
                    "relevance": "same_directory"
                })

        return related[:max_files]

    
    def build_context(self, current_file: str, selected_code: str) -> str:

        """Build context from related files"""
        context_parts = [f"Current file: {current_file}\n"]
        related = self.get_related_files(current_file)

        for file_info in related:
            try:
                with open(file_info['path'], 'r') as f:
                    content = f.read()
                    # Get just the function signatures for context
                    signatures = self.extract_signatures(content)
                    if signatures:
                        context_parts.append(
                            f"\nFrom {file_info['path']} ({file_info['relevance']}):\n"
                            + "\n".join(signatures)
                            )
            except Exception:
                continue

        return "\n".join(context_parts)

    
    def extract_signatures(self, code: str) -> List[str]:

        """Extract function and class signatures"""
        signatures = []
        lines = code.split('\n')

        for i, line in enumerate(lines):
            if line.strip().startswith(('def ', 'class ')):
                # Get the full signature including decorators
                sig_lines = [line]
                 # Look for decorators above
                j = i - 1
                while j >= 0 and lines[j].strip().startswith('@'):
                    sig_lines.insert(0, lines[j])
                    j -= 1
                 # Look for continuation lines
                if line.rstrip().endswith(':'):
                    signatures.append('\n'.join(sig_lines))
                else:
                    # Multi-line signature
                    j = i + 1
                    while j < len(lines) and not lines[j].rstrip().endswith(':'):
                        sig_lines.append(lines[j])
                        j += 1
                    if j < len(lines):
                       sig_lines.append(lines[j])
                    signatures.append('\n'.join(sig_lines))

        return signatures