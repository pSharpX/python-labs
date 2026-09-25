import json
import os
import re

from dotenv import load_dotenv

from exa_py import Exa
from langchain_core.tools import tool

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
exa_api_key = os.getenv("EXA_API_KEY")


exa = Exa(api_key=exa_api_key)


def limpiar_texto(text: str) -> str:
    """
    Limpia el texto extraído de una noticia.

    - Elimina enlaces Markdown.
    - Elimina URLs sueltas.
    - Reemplaza saltos de línea.
    - Compacta espacios múltiples.
    """

    if not text:
        return ""

    # Eliminar enlaces Markdown: [texto](url) -> texto
    text = re.sub(
        r"\[([^\]]+)\]\([^)]+\)",
        r"\1",
        text
    )

    # Eliminar URLs sueltas
    text = re.sub(
        r"http\S+",
        "",
        text
    )

    # Reemplazar saltos de línea
    text = text.replace("\n", " ")

    # Compactar espacios
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()

@tool("buscar_noticias")
def web_scraping(consulta: str) -> str:
    """
    Busca y analiza noticias en medios peruanos como
    La República y El Comercio.

    Utiliza esta herramienta para:
    - buscar noticias;
    - investigar acontecimientos recientes;
    - responder preguntas de actualidad;
    - verificar afirmaciones;
    - realizar fact-checking.

    La entrada debe ser la pregunta o afirmación
    que se desea investigar.
    """

    try:

        # ====================================================
        # 1. BÚSQUEDA CON EXA
        # ====================================================

        result_web = exa.search(
            consulta,
            include_domains=[
                "larepublica.pe",
                "elcomercio.pe",
            ],
            num_results=3,
            type="auto",
            user_location="PE",
            contents={
                "text": {
                    "maxCharacters": 8000
                },

                # Permite utilizar contenido reciente.
                # Si la copia tiene más de 24 h,
                # Exa puede volver a recuperarla.
                "maxAgeHours": 24, #4380
            },
        )

        # ====================================================
        # 2. PROCESAR RESULTADOS
        # ====================================================

        data = []
        for resultado in result_web.results:
            texto = limpiar_texto(
                getattr(
                    resultado,
                    "text",
                    ""
                ) or ""
            )

            # Ignorar resultados sin contenido
            if not texto:
                continue
            data.append(
                {
                    "url": getattr(
                        resultado,
                        "url",
                        ""
                    ),
                    "title": getattr(
                        resultado,
                        "title",
                        ""
                    ),
                    "published_date": (
                        getattr(
                            resultado,
                            "published_date",
                            None
                        )
                        or "Fecha no disponible"
                    ),

                    "text": texto,
                }
            )


        # ====================================================
        # 3. VALIDAR RESULTADOS
        # ====================================================

        if not data:
            return (
                f"No se encontraron noticias con información suficiente "
                f"para la consulta: '{consulta}'. "
                "No es posible verificar la afirmación o responder "
                "la pregunta con las fuentes consultadas."
            )
        text = json.dumps(data, ensure_ascii=False)
        return text
    except Exception as error:
        print(error)
        return (
            "Ocurrió un error durante la búsqueda de noticias. "
            f"Tipo de error: {type(error).__name__}. "
            "No fue posible obtener evidencia en este momento."
        )