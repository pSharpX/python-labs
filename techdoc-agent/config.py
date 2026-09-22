from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer


serde = JsonPlusSerializer(
    allowed_msgpack_modules=[
        ("src.state.requirements.models", "Actor"),
        ("src.state.requirements.models", "Process"),
        ("src.state.requirements.models", "MissingInformation"),
        ("src.state.requirements.models", "Requirement"),
    ]
)