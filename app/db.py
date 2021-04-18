from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker, Session as OrmSession
from sqlalchemy import create_engine

import config


engine = create_engine(config.SQLALCHEMY_DATABASE_URI, executemany_mode="batch")
Session = sessionmaker(bind=engine)


@contextmanager
def session_scope() -> OrmSession:
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
