from datetime import datetime

from sqlalchemy import Column, Integer, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from schema import Base


class Contract(Base):
    """
    Represents a Contract between two Players in a Game.

    Contracts usually go through two of the following statuses

        Open         The killer still has time to complete the Contract
        Completed    The killer successfully killed his target
        Expired      The killed did not complete the Contract in time
        Uncompleted  The target was killed before Contract completion
        Stolen       Another Player killed the target
    """

    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True)

    status = Column(
        Enum('open', 'expired', 'uncompleted', 'completed', 'stolen',
             name='contract_status'),
        default='open', nullable=False)
    assignment_date = Column(
        DateTime(), nullable=False, default=datetime.utcnow)
    conclusion_date = Column(DateTime())

    killer_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    target_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)

    killer = relationship(
        "Player", backref='all_contracts',
        primaryjoin="Player.id==Contract.killer_id")
    target = relationship(
        "Player", backref='all_target_of_contracts',
        primaryjoin="Player.id == Contract.target_id")
    game = relationship(
        "Game", backref='contracts',
        primaryjoin=(
            "(Game.id == Contract.game_id) &"
            "(Contract.status=='open')"))

    def __init__(self, killer, target):
        """ Create a new Contract. """

        assert not killer.id == target.id
        assert not target.id in [t.id for t in killer.targets]

        self.killer_id = killer.id
        self.target_id = target.id
        self.game_id = killer.game.id

    def conclude(self, status):
        """
        Conclude a contract. Does not do anything to the target of the
        contract.
        """

        assert self.status == 'open'
        assert status in ['expired', 'uncompleted', 'completed', 'stolen']

        self.status = status
        self.conclusion_date = datetime.utcnow()

    def __repr__(self):
        return "<Contract('%s', '%s', '%s')>" % (
            (self.killer_id, self.target_id, self.status))
