
class Book:
    id: int
    title: str
    author: str
    category: str
    rating: int

    def __init__(self, id, title, author, category, rating):
        self.id = id
        self.title = title
        self.author = author
        self.category = category
        self.rating = rating