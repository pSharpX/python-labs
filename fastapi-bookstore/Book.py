
class Book:
    id: int
    title: str
    author: str
    category: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, category, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.category = category
        self.rating = rating
        self.published_date = published_date