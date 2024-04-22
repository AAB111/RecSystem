from sqlalchemy import text
from sqlalchemy.sql import DDL

def create_update_latest_activity_user():
    ddl_function = DDL("""
    CREATE OR REPLACE FUNCTION rec_movies.update_latest_activity_user() RETURNS TRIGGER AS $$
    BEGIN
        UPDATE "User" SET latest_activity = NEW.datetime_added WHERE id = NEW.user_id;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)
    return ddl_function

def create_update_latest_activity_review():
    ddl_function = DDL("""
    CREATE OR REPLACE FUNCTION rec_movies.update_latest_activity_review() RETURNS TRIGGER AS $$
    BEGIN
        UPDATE "Review" SET latest_change = NOW() WHERE (user_id = NEW.user_id) & (movie_id = NEW.movie_id);
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)
    return ddl_function