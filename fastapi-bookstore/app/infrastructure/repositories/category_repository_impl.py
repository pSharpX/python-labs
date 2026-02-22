from sqlalchemy.orm import Session
from app.domain.entities import Category
from app.domain.repositories import CategoryRepository
from app.infrastructure.models import CategoryModel

class CategoryRepositoryImpl(CategoryRepository):

    def __init__(self, db: Session):
        self.db = db

    def create(self, category: Category) -> Category:
        db_category = CategoryModel(name=category.name, description=category.description)
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)

        return Category(id=db_category.id, name=db_category.name, description=db_category.description)

    def get_by_id(self, book_id: int):
        db_category = self.db.query(CategoryModel).filter_by(id = id).first()
        if not db_category:
            return None
        return Category(id=db_category.id, name=db_category.name, description=db_category.description)
