from pathlib import Path
from typing import Type

from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool


class SaveMarkdownInput(BaseModel):
    content: str = Field(
        description="Contenido en formato Markdown que se guardará en el archivo."
    )
    filename: str = Field(
        description="Nombre del archivo Markdown que se creará, incluyendo la extensión .md."
    )


class SaveMarkdownTool(BaseTool):
    name: str = "save_markdown"
    description: str = (
        "Crea un archivo Markdown y guarda en él el contenido proporcionado. "
        "Utiliza esta herramienta cuando el usuario solicite guardar, exportar "
        "o persistir contenido en formato Markdown como un archivo local .md."
    )
    args_schema: Type[BaseModel] = SaveMarkdownInput

    output_dir: str = "./docs/outcomes"

    def _run(self, content: str, filename: str) -> str:
        output_path = Path(self.output_dir) / filename

        # Ensure the output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure the file has a .md extension
        if output_path.suffix.lower() != ".md":
            output_path = output_path.with_suffix(".md")

        output_path.write_text(content, encoding="utf-8")

        return f"Markdown file successfully saved to: {output_path}"