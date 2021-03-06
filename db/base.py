# -*- coding: utf-8 -*-
import logging
from collections import namedtuple
from contextlib import contextmanager

import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base


logger = logging.getLogger(__name__)


metadata = sa.MetaData()
Session = so.scoped_session(so.sessionmaker())

Base = declarative_base(metadata=metadata)


@contextmanager
def session(close=True, remove=False, **kwargs):
    """Provide a transactional scope around a series of operations."""
    new_session = Session(**kwargs)
    try:
        logger.info("Yield session %s", id(new_session))
        yield new_session
        new_session.commit()
        logger.info("Commited..")
    except SQLAlchemyError as err:
        logger.exception("SQLAlchemyError error, rollback!")
        new_session.rollback()
        raise err
    finally:
        if close:
            logger.info("Close session %s", id(new_session))
            new_session.close()
        if remove:
            logger.info("Remove session %s", id(new_session))
            Session.remove()


def init_db(engine=None):

    if engine is None:
        engine = sa.create_engine("sqlite://")

    from . import schema
    DB = namedtuple("DB", ["session"] + schema.__all__)

    Session.configure(bind=engine)
    metadata.bind = engine
    metadata.create_all()
    logger.info("Init database with metadata: %s", metadata)

    db_items = [getattr(schema, t, None) for t in schema.__all__]
    # noinspection PyArgumentList
    return DB(session, *db_items)
