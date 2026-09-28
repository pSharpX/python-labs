from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer


serde = JsonPlusSerializer(
    allowed_msgpack_modules=[
        ("src.state.models", "Actor"),
        ("src.state.models", "Process"),
        ("src.state.models", "MissingInformation"),
        ("src.state.models", "Requirement"),
        ("src.state.models", "Requirements"),
    ]
)