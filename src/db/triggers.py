from sqlalchemy import event, DDL, Table
from src.db.functions_db import create_update_latest_activity_user, create_update_latest_activity_review


@event.listens_for(Table, "after_insert")
def update_latest_activity_after_create(target, connection, **kw):
    if target.name == 'MovieWatched':
        connection.execute(create_update_latest_activity_user())
        ddl_trigger = DDL("""
        CREATE TRIGGER update_latest_activity_user
        AFTER INSERT ON rec_movies."MovieWatched"
        FOR EACH ROW EXECUTE FUNCTION rec_movies.update_latest_activity_user();
        """)
        connection.execute(ddl_trigger)
    if target.name == 'MovieBeWatching':
        connection.execute(create_update_latest_activity_user())
        ddl = DDL("""
        CREATE TRIGGER update_latest_activity_user
        AFTER INSERT ON rec_movies."MovieBeWatching"
        FOR EACH ROW EXECUTE FUNCTION rec_movies.update_latest_activity_user();
        """)
        connection.execute(ddl)
    if target.name == 'MovieNegative':
        connection.execute(create_update_latest_activity_user())
        ddl_trigger = DDL("""
        CREATE TRIGGER update_latest_activity_user
        AFTER INSERT ON rec_movies."MovieNegative"
        FOR EACH ROW EXECUTE FUNCTION rec_movies.update_latest_activity_user();
        """)
        connection.execute(ddl_trigger)
    if target.name == 'MovieEvaluated':
        connection.execute(create_update_latest_activity_user())
        ddl_trigger = DDL("""
        CREATE TRIGGER update_latest_activity_user
        AFTER INSERT ON rec_movies."MovieEvaluated"
        FOR EACH ROW EXECUTE FUNCTION rec_movies.update_latest_activity_user();
        """)
        connection.execute(ddl_trigger)
    if target.name == 'Review':
        connection.execute(create_update_latest_activity_user())
        ddl_trigger = DDL("""
        CREATE TRIGGER update_latest_activity_user
        AFTER INSERT ON rec_movies."Review"
        FOR EACH ROW EXECUTE FUNCTION rec_movies.update_latest_activity_user();
        """)
        connection.execute(ddl_trigger)


@event.listens_for(Table, "after_update")
def update_latest_activity_after_update(target, connection, **kw):
    if target.name == 'Review':
        connection.execute(create_update_latest_activity_user())
        connection.execute(create_update_latest_activity_review())
        ddl = DDL("""CREATE TRIGGER update_latest_activity_user_review
                  AFTER UPDATE ON rec_moves."Review" FOR EACH ROW 
                  EXECUTE FUNCTION rec_movies.create_update_latest_activity_review(),
                  EXECUTE FUNCTION rec_movies.create_update_latest_activity_user();""")
        connection.execute(ddl)
    if target.name == 'MovieEvaluated':
        connection.execute(create_update_latest_activity_user())
        ddl = DDL("""CREATE TRIGGER update_latest_activity_user_after_update
                    AFTER UPDATE ON rec_movies."MovieEvaluated" FOR EACH ROW
                    EXECUTE FUNCTION rec_movies.create_update_latest_activity_user();""")
        connection.execute(ddl)


@event.listens_for(Table, "after_delete")
def update_latest_activity_after_delete(target, connection, **kw):
    if target.name == 'Review':
        connection.execute(create_update_latest_activity_user())
        ddl = DDL("""CREATE TRIGGER update_latest_activity_user_after_delete 
                    AFTER DELETE ON rec_moves."Review" FOR EACH ROW 
                    EXECUTE FUNCTION rec_movies.create_update_latest_activity_user();
                  """)
        connection.execute(ddl)
    if target.name == 'MovieNegative':
        connection.execute(create_update_latest_activity_user())
        ddl = DDL("""CREATE TRIGGER update_latest_activity_user_after_delete
                    AFTER DELETE ON rec_movies."MovieNegative" FOR EACH ROW
                    EXECUTE FUNCTION rec_movies.create_update_latest_activity_user();""")
        connection.execute(ddl)
    if target.name == 'MovieBeWatching':
        connection.execute(create_update_latest_activity_user())
        ddl = DDL("""CREATE TRIGGER update_latest_activity_user_after_delete
                    AFTER DELETE ON rec_movies."MovieBeWatching" FOR EACH ROW
                    EXECUTE FUNCTION rec_movies.create_update_latest_activity_user();""")
        connection.execute(ddl)
    if target.name == 'MovieWatched':
        connection.execute(create_update_latest_activity_user())
        ddl = DDL("""CREATE TRIGGER update_latest_activity_user_after_delete
                    AFTER DELETE ON rec_movies."MovieWatched" FOR EACH ROW
                    EXECUTE FUNCTION rec_movies.create_update_latest_activity_user();""")
        connection.execute(ddl)
    if target.name == 'MovieEvaluated':
        connection.execute(create_update_latest_activity_user())
        ddl = DDL("""CREATE TRIGGER update_latest_activity_user_after_delete
                    AFTER DELETE ON rec_movies."MovieEvaluated" FOR EACH ROW
                    EXECUTE FUNCTION rec_movies.create_update_latest_activity_user();""")
        connection.execute(ddl)
