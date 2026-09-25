from pydantic import BaseModel


from pydantic import BaseModel, Field


class ResumenPeriodisticoOutput(BaseModel):
    resumen: str = Field(
        description=(
            "Guion narrativo periodístico breve elaborado a partir de las "
            "noticias seleccionadas. Debe sintetizar los hechos más relevantes "
            "de forma clara, objetiva, coherente y verificable. Debe incluir "
            "el contexto necesario y estar redactado con un estilo natural "
            "y fluido, adecuado para ser leído por una voz. No debe inventar "
            "datos ni introducir opiniones no respaldadas por las fuentes."
        )
    )

    prompts: list[str] = Field(
        description=(
            "Lista de prompts descriptivos para generar imágenes mediante IA "
            "que ilustren visualmente los principales hechos narrados en el "
            "guion. Cada prompt debe describir una escena concreta, relevante "
            "para la noticia y coherente con la información disponible, sin "
            "inventar personas, eventos o detalles que no estén respaldados "
            "por las fuentes."
        )
    )