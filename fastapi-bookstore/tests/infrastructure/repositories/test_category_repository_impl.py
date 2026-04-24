import pytest

from app.domain.entities import Category
from app.domain.repositories import CategoryRepository
from app.infrastructure.models import CategoryModel
from app.infrastructure.repositories import CategoryRepositoryImpl

categories = [
    Category(id=None, name="Test Category 1", description="Test Category"),
    Category(id=None, name="Test Category 2", description="Test Category"),
    Category(id=None, name="Test Category 3", description="Test Category"),
    Category(id=None, name="Test Category 4", description="Test Category"),
    Category(id=None, name="Test Category 5", description=None),
    Category(id=None, name="Test Category 6", description=None),
    Category(id=None, name="Test Category 7", description=None),
    Category(id=None, name="Test Category 8", description="Test Category"),
    Category(id=None, name="Test Category 9", description="Test Category"),
    Category(id=None, name="Test Category 10", description="Test Category")
]

invalid_categories = [
    Category(id=None, name="Test Category 2", description="Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category "
                                                          "Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category "
                                                          "Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category "
                                                          "Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category "
                                                          "Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category "
                                                          "Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category "
                                                          "Test Category Test Category Test Category Test Category Test Category Test Category"),
    Category(id=None, name="Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category Test Category", description=None),
    Category(id=None, name=None, description="Test Category"),
    Category(id=None, name=None, description=None),
]

class TestCategoryRepositoryImpl:
    category_id: int
    repository: CategoryRepository

    @pytest.fixture
    def default_category(self):
        return Category(id=None, name="Test Category", description="Test Category")

    @pytest.mark.parametrize("new_category", categories)
    def test_create_category(self, mocker, get_db, new_category):
        add_spy = mocker.spy(get_db, 'add')
        commit_spy = mocker.spy(get_db, 'commit')
        refresh_spy = mocker.spy(get_db, 'refresh')
        self.repository = CategoryRepositoryImpl(get_db)

        category = self.repository.create(new_category)

        assert category is not None
        assert isinstance(category, Category)
        assert category.id is not None
        assert category.name == new_category.name
        assert category.description == new_category.description

        args, kwargs = refresh_spy.call_args
        category_model = args[0]
        assert category_model is not None
        assert isinstance(category_model, CategoryModel)

        add_spy.assert_called_once()
        commit_spy.assert_called_once()
        refresh_spy.assert_called_once()

    @pytest.mark.parametrize("invalid_category", invalid_categories)
    def test_create_category_with_invalid_data(self, mocker, get_db, invalid_category):
        add_spy = mocker.spy(get_db, 'add')
        commit_spy = mocker.spy(get_db, 'commit')
        refresh_spy = mocker.spy(get_db, 'refresh')
        self.repository = CategoryRepositoryImpl(get_db)

        with pytest.raises(Exception):
            self.repository.create(invalid_category)

        args, kwargs = add_spy.call_args
        category_model = args[0]
        assert category_model is not None
        assert isinstance(category_model, CategoryModel)

        add_spy.assert_called_once()
        commit_spy.assert_called_once()
        refresh_spy.assert_not_called()

    def test_get_by_id_category(self, mocker, get_db, default_category):
        query_spy = mocker.spy(get_db, 'query')
        self.repository = CategoryRepositoryImpl(get_db)

        category = self.repository.create(default_category)
        existent_category = self.repository.get_by_id(category.id)

        assert existent_category is not None
        assert isinstance(existent_category, Category)
        assert existent_category.id is not None
        assert existent_category.name == default_category.name
        assert existent_category.description == default_category.description

        query_spy.assert_called_once_with(CategoryModel)

    def test_get_by_id_category_unexistent(self, mocker, get_db):
        query_spy = mocker.spy(get_db, 'query')
        self.repository = CategoryRepositoryImpl(get_db)

        unexistent_category = self.repository.get_by_id(10000)

        assert unexistent_category is None

        query_spy.assert_called_once_with(CategoryModel)