from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Enum, DateTime, ForeignKey, CheckConstraint)
from sqlalchemy.orm import relationship

from bloodtide.util import slugify
from schema import Base


class Game(Base):
    """
    Represents a Game. Each Player in a Game is owned by a User. A Game
    is owned and created by a User.

    A Game usually goes through four of the following statutes

        Unapproved  The game has not been paid for or approved by staff.
        Approved    The game has been payed for or approved by staff.
        Rejected    The staff specifically denied the games approval.
        Active      The game was approved and the owner has started it.
        Completed   The game came to it's normal conclusion.
        Shutdown    The game was shutdown by staff before it could conclude.

    Currently, Users need the Game's id and join_code to become part of
    a Game and have a Player created for them. This may change in the
    future.

    The Game description should provide users additional information
    identifying the game, such the location or social group the game is
    being played among.

    The rules of the Game should expand on the default rules of a Game
    type.
    """

    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)

    name = Column(
        String(24), CheckConstraint('char_length(name)>=8'), nullable=False,
        unique=True)
    slug = Column(String(24), nullable=False, unique=True)
    rules = Column(String, nullable=False)
    description = Column(String, nullable=False)
    join_code = Column(
        String(6), CheckConstraint('char_length(join_code)=6'), unique=True)
    status = Column(
        Enum('unapproved', 'approved', 'active', 'completed', 'rejected',
             'shutdown', name='game_status'),
        default='unapproved', nullable=False)

    creation_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    # The date of approval or rejection.
    approval_date = Column(DateTime)
    commencement_date = Column(DateTime)

    # The date of normal or abnormal conclusion.
    conclusion_date = Column(DateTime)

    # By default, the owner is the creator.
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # `creator' and `owner' are defined in user.User
    players = relationship("Player", backref="game")

    def __init__(self, creator, name, description, rules):
        """ Create a new Game. """

        assert not creator.user_type == 'half'

        self.creator_id = creator.id
        self.owner_id = self.creator_id
        self.name = name
        self.slug = slugify(name)
        self.description = description
        self.rules = rules
        # TODO: Actually generate a code.
        self.join_code = "ABCDEF"  # generate_code(6)

    @property
    def state(self):
        """
        This function groups the statuses of a Game into more general
        states.

        Unapproved or approved returns 'pregame'. Active returns
        'active'. Rejected, shutdown, or completed return 'inactive'.
        """

        if self.status in ['unapproved', 'approved']:
            return 'pregame'
        elif self.status in ['rejected', 'shutdown', 'completed']:
            return 'inactive'
        elif self.status == 'active':
            return 'active'

    def set_status(self, status):
        """ Set the status of a Game. """

        if status == 'approved':
            assert self.status == 'unapproved'
            self.approval_date = datetime.utcnow()

        elif status == 'rejected':
            assert self.status == 'unapproved'
            self.approval_date = datetime.utcnow()

        elif status == 'active':
            assert self.status == 'approved'
            self.commencement_date = datetime.utcnow()

        elif status == 'completed':
            assert self.status == 'active'
            self.conclusion_date = datetime.utcnow()

        elif status == 'shutdown':
            assert self.status == 'active'
            self.conclusion_date = datetime.utcnow()

        self.status = status

    def __repr__(self):
        return "<Game('%s', '%s', '%s', '%s')>" % (
            (self.id, self.name, self.status, self.owner.name()))
