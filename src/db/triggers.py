from sqlalchemy import event, DDL
from src.db.functions_db import (create_update_latest_activity_user)
from src.db.models import Base


@event.listens_for(Base, "after_insert")
def update_latest_activity_after_create(target, connection, **kw):
    tables_after_insert = ['MovieWatched', 'MovieBeWatching', 'MovieNegative', 'MovieEvaluated', 'Review']
    if target.name in tables_after_insert:
        ddl_trigger = DDL(f"""
                    CREATE TRIGGER update_latest_activity_user
                    AFTER INSERT ON rec_movies."{target.name}"
                    FOR EACH ROW EXECUTE FUNCTION rec_movies.update_latest_activity_user();
                    """)
        connection.execute(ddl_trigger)


@event.listens_for(Base, "after_update")
def update_latest_activity_after_update(target, connection, **kw):
    if target.name == 'Review':
        connection.execute(create_update_latest_activity_user())

        ddl_user = DDL("""
            CREATE TRIGGER update_latest_activity_user_after_update
            AFTER UPDATE ON rec_movies."Review" 
            FOR EACH ROW 
            EXECUTE FUNCTION rec_movies.update_latest_activity_user();
            """)

        connection.execute(ddl_user)
    if target.name == 'MovieEvaluated':
        connection.execute(create_update_latest_activity_user())
        ddl_user = DDL("""
                    CREATE TRIGGER update_latest_activity_user_after_update
                    AFTER UPDATE ON rec_movies."MovieEvaluated" 
                    FOR EACH ROW 
                    EXECUTE FUNCTION rec_movies.update_latest_activity_user();
                    """)

        connection.execute(ddl_user)


@event.listens_for(Base, "after_delete")
def update_latest_activity_after_delete(target, connection, **kw):
    tables_after_insert = ['MovieWatched', 'MovieBeWatching', 'MovieNegative', 'MovieEvaluated', 'Review']
    if target.name in tables_after_insert:
        ddl = DDL(f"""CREATE TRIGGER update_latest_activity_user_after_delete 
                    AFTER DELETE ON rec_moves."{target.name}" FOR EACH ROW 
                    EXECUTE FUNCTION rec_movies.create_update_latest_activity_user();
                  """)
        connection.execute(ddl)
