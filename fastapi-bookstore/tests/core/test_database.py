import sqlalchemy

def test_database_connection(mysql_container):
    engine = sqlalchemy.create_engine(mysql_container)
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT 1"))
        assert result.fetchone()[0] == 1

