from datetime import datetime

from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime, \
    CheckConstraint
from sqlalchemy.orm import relationship

from schema import Base


class User(Base):
    """
    Represents a User account on bloodtide.net. A User account is tied
    to a unique phone number. Users can be full, half, or staff.

    A full User can log into the website using a password, create games,
    and become a Game moderator.

    A half User can participate in Games using SMS but cannot access
    the website. A half User can become a full User by adding a
    password to their account.

    A staff User is a member of the bloodtide staff. These Users can
    log into the administrative interface and manage Games.

    Users can have their account banned, meaning that they cannot login
    or participate in ANY games. This is not the same as banning phone
    numbers.
    """

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)

    fname = Column(String(32), nullable=False)
    lname = Column(String(32), nullable=False)
    user_type = Column(
        Enum('administrator', 'moderator', 'full', 'half', name="user_type"),
        nullable=False)
    number_verified = Column(Boolean, default=False, nullable=False)
    phone_number = Column(
        String(16),
        CheckConstraint('char_length(phone_number)>=7'),
        nullable=False, unique=True)

    # join_date for half users is the time a User row is added to the database
    # for full users, when validated becomes true
    join_date = Column(DateTime())
    verification_code = Column(String(6))
    password = Column(String)
    banned = Column(Boolean, default=False, nullable=False)

    created_games = relationship(
        "Game", backref="creator", primaryjoin="User.id==Game.creator_id")
    owns_games = relationship(
        "Game", backref="owner", primaryjoin="User.id==Game.owner_id")
    players = relationship("Player", backref="user")

    def __init__(self, phone_number, fname, lname, user_type, **kwargs):
        """
        Create one of three types of Users: half, full, or staff.

        All Users require a phone_number, first name, and last name.

        Full Users and staff require a kwarg `password' that has already
        been hashed.

        Valid user_types are: 'half', 'full', 'moderator', or
        'administrator'.
        """

        assert user_type in ['half', 'full', 'administrator', 'moderator']

        self.phone_number = phone_number
        self.fname = fname
        self.lname = lname

        if user_type == 'half':
            self.user_type = 'half'
            self.join_date = datetime.utcnow()
            self.number_verified = True

        else:
            assert kwargs.get('password') is not None

            self.password = kwargs.get('password')
            self.user_type = user_type
            # TODO: Actual verification code.
            self.verification_code = "abcdef"  # generate_code(6).lower()
            self.number_verified = False

    def name(self):
        """ First + last names properly capitalized. """
        return "%s %s" % (self.fname.capitalize(), self.lname.capitalize())

    def verify_number(self):
        """
        Verifies a User's phone_number. This method assumes that a user
        has already provided a valid verification code.
        """

        assert self.number_verified is False
        assert self.user_type in ['full', 'moderator', 'administrator']

        self.number_verified = True
        self.verification_code = None
        self.join_date = datetime.utcnow()

    def player_in(self, game):
        """ Returns True if this User is a Player of the Game. """
        return game.id in [p.game_id for p in self.players]

    def player_type_in(self, game, ptype='administrator'):
        """
        Returns True if this User is a Player of a specific Type of
        Game.

        Valid types are: 'administrator', 'moderator', 'normal', or
        'banned'.
        """

        assert ptype in ['administrator', 'moderator', 'normal', 'banned']

        return game.id in (
            [p.game_id for p in self.players if p.player_type == ptype])

    # The next 4 methods implement the FlaskLogin interface.
    # TODO: Flask login isn't used yet.
    # def is_authenticated(self):
    #     return True

    # def is_active(self):
    #     return not self.banned

    # def is_anonymous(self):
    #     return False

    # def get_id(self):
    #     return unicode(self.id)

    def __repr__(self):
        return "<User('%s', '%s, '%s', '%s')>" % (
            (self.id, self.name(), self.phone_number, self.user_type))
