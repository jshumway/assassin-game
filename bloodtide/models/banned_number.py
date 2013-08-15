from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint

from schema import Base


class BannedNumber(Base):
    """
    These numbers are never allowed to register on the webiste or participate
    in any games in any way. If possible, they should be banned from sending
    messages through Twilio as well.
    """

    __tablename__ = 'banned_numbers'

    id = Column(Integer, primary_key=True)

    banned_date = Column(DateTime(), nullable=False, default=datetime.utcnow)
    phone_number = Column(
        String(16), CheckConstraint('char_length(phone_number)>=7'),
        nullable=False, unique=True)

    notes = Column(String)

    def __init__(self, phone_number, notes=None):
        self.phone_number = phone_number
        self.notes = notes

    def __repr__(self):
        return "<BannedNumber('%s', '%s')>" % (self.id, self.phone_number)
