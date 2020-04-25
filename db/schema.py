import logging
from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as so

from .base import Base, Session

__all__ = ["User", "Message"]

logger = logging.getLogger(__name__)


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    nickname = sa.Column(sa.String, unique=True)
    first_name = sa.Column(sa.String, nullable=True)
    last_name = sa.Column(sa.String, nullable=True)
    utc_created_at = sa.Column(sa.DateTime, default=datetime.utcnow)

    messages = so.relationship("Message", lazy='dynamic')

    query = Session.query_property()

    def __init__(self, nickname, first_name=None, last_name=None):
        self.nickname = nickname
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return "<User({s.id!r}, {s.nickname!r})>".format(s=self)

    def __str__(self):
        full_name = ""
        if self.first_name:
            full_name += self.first_name
        if self.last_name:
            if full_name:
                full_name += " "
            full_name += self.last_name
        return full_name or self.nickname

    @classmethod
    def get_or_create(cls, nickname, **kwargs):
        user = cls.query.filter(cls.nickname == nickname).one_or_none()
        if user is None:
            user = cls(nickname, **kwargs)
            Session.add(user)
            Session.flush()
            logger.info("Created %r", user)
        else:
            logger.debug("Got %r", user)
        return user

    def create_message(self, text):
        return Message.create(self.id, str(text))


class Message(Base):
    __tablename__ = "messages"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id, ondelete="CASCADE"), nullable=False)
    text = sa.Column(sa.String, default=str)
    utc_created_at = sa.Column(sa.DateTime, default=datetime.utcnow)

    query = Session.query_property()

    def __init__(self, user_id, text):
        self.user_id = user_id
        self.text = text

    def __repr__(self):
        return "<Message({s.id!r}, {s.user_id!r}, {s.text!r})>".format(s=self)

    def __str__(self):
        return self.text

    @classmethod
    def create(cls, user_id, text):
        message = cls(user_id, text)
        Session.add(message)
        Session.flush()
        logger.info("Created %r", message)
        return message
