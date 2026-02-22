from dataclasses import dataclass

@dataclass
class Author:
    id: int
    name: str
    fullname: str

    def __init__(self, id, name, fullname):
        self.id = id
        self.name = name
        self.fullname = fullname