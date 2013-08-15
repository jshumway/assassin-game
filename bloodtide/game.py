"""
A higher level interface to start and interact with a game of
bloodtide.
"""

# TODO: Merge this file with base_game.py?

from bloodtide.base_game import (
    init_game, kill_player, new_contract, resurrect_player)
from bloodtide.models import Game, Player


def create_game(session, creator, name, description, rules):
    """
    Create a new game with User |creator| as the initial creator and
    owner.

    Adds new game to |session| and flushes it.

    Return the new game and the Player associated with |creator|.
    """

    assert creator.user_type != 'half'

    game = Game(creator, name, description, rules)
    session.add(game)
    session.flush()

    player = Player(creator, game, status='administrator')

    return game, player


def join_game(game, user):
    """
    Add User |user| to Game |game|. |game| must not be started.

    A user joining a game really means having a new Player created to
    associate |user| with |game|.

    Return the new Player.
    """

    assert game.state == 'pregame'

    return Player(user, game)


def start_game(session, game):
    """
    Start |game|, initializing players and creating contracts. Adds all
    initials contracts to |session| and commits.
    """

    session.add_all(init_game(game))
    session.commit()


def end_game(game):
    """
    Bring a game to its normal close.

    Kills all players in the game, closes all open contracts as
    incompleted.
    """

    assert game.state == 'active'

    game.set_status('completed')

    for player in game.players:
        if player.alive:
            player.kill()

            for contract in player.contracts:
                contract.conclude('incompleted')


def handle_kill(session, game, player, target, contract):
    """
    |player| kills |target| and is assigned a new contract. All players
    that had a contract stolen also have a new contract created for
    them.

    Adds newly created contracts to |session| and commits.
    """

    print('handle kill')

    stolen_contracts = kill_player(player, target, contract)
    new_contracts = []

    print('\tthe following were stolen contracts')
    for contract in stolen_contracts:
        print('\t\t%s' % contract)

    for contract in stolen_contracts:
        c = new_contract(game, contract.killer)
        if not c is None:
            print('\tcreate %s for stolen' % c)
            session.add(c)

    player_contract = new_contract(game, player)

    # The player is the last man standing.
    if not player_contract:
        assert not new_contracts
        session.commit()
        return

    print('\tcreate %s for player' % player_contract)
    session.add(player_contract)
    session.commit()


def resurrect_all(session, game):
    """
    Resurrect all players in |game| and assign contracts as
    appropriate.
    """

    # TODO: Can't handle multiple contracts.
    for player in game.players:
        if not player.alive:
            resurrect_player(player)

    session.flush()

    for player in game.players:
        if len(player.contracts) == 0:
            session.add(new_contract(game, player))

    session.commit()
