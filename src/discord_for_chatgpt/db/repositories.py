from sqlalchemy import text

from .models import Base


class Repository:
    def __init__(self, session):
        self.session = session
