from datetime import datetime

from sqlalchemy import Column, Boolean, Integer, String, Enum, DateTime, \
    ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from schema import Base


class Player(Base):
    """
    Represents a User's activity in a Game. Players can have different
    statuses within a Game: 'administrator', 'moderator', 'normal',
    'banned'.
    """

    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)

    status = Column(
        Enum('administrator', 'moderator', 'normal', 'banned',
             name='status'),
        default='normal', nullable=False)

    alive = Column(Boolean, default=False, nullable=False)
    auto_resurrect = Column(Boolean, default=True, nullable=False)
    life_id = Column(
        String(6), CheckConstraint('char_length(life_id)=6'), unique=True)

    game_entry_time = Column(
        DateTime(), default=datetime.utcnow, nullable=False)
    last_alive_time = Column(DateTime())
    last_respawn_time = Column(DateTime())

    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Players in a game have a self-referential many-to-many relationship
    # defined by contracts. The following 3 relationships only include open
    # Contracts
    targets = relationship(
        'Player', secondary='contracts',
        primaryjoin=(
            "(contracts.c.status=='open') &"
            "(Player.id==contracts.c.killer_id)"),
        secondaryjoin=(
            "(Player.id==contracts.c.target_id) &"
            "(contracts.c.status=='open')"),
        backref='target_of')

    contracts = relationship(
        'Contract',
        primaryjoin=(
            "(Player.id==Contract.killer_id) & (Contract.status=='open')"))

    # A list of all the open Contracts which have this Player as a target.
    target_of_contracts = relationship(
        'Contract',
        primaryjoin=(
            "(Player.id==Contract.target_id) & (Contract.status=='open')"))

    def __init__(self, user, game, status='normal'):
        """ Create a new Player. """

        assert status in ['normal', 'moderator', 'administrator']

        self.user_id = user.id
        self.game_id = game.id
        self.status = status

    def resurrect(self, life_id):
        """
        Bring a fallen Player back to life. This function consider
        Player.auto_resurrect.
        """

        assert self.alive is False

        self.alive = True
        self.last_respawn_time = datetime.utcnow()
        self.last_alive_time = None
        self.life_id = life_id

    def kill(self):
        """ Mark a Player as dead. Does not deal with Contracts at all. """

        assert self.alive is True

        self.alive = False
        self.last_alive_time = datetime.utcnow()
        self.last_respawn_time = None
        self.life_id = None

    def __repr__(self):
        return "<Player(%s, '%s', '%s', %s)>" % (
            (self.id, self.user.name(), self.status, self.alive))
