from dataclasses import dataclass

@dataclass
class Category:
    id: int
    name: str
    description: str

    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description