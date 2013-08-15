"""
Run a simulation of a Bloodtide game.
"""

from operator import attrgetter
import random

from sqlalchemy import create_engine

from bloodtide.base_game import new_contract
from bloodtide.game import (
    create_game, join_game, handle_kill, start_game, resurrect_all)
from fixtures import create_users


def setup_everything(session, player_count):
    """
    Setup everything needed to simulate a game. Creates |player_count|
    users, one of which is a full user, who creates a game. The other
    users join the game. Game is set to 'approved' state.

    All users, players, and the game are committed to the |session|.

    Return the game, the users, and the players.
    """

    # Create a bunch of users
    users = create_users(player_count)
    session.add_all(users)
    session.flush()

    # have one create a game
    game, creator = create_game(
        session, users[0], 'this is totes a game', 'hi', 'hi')
    session.add(game)
    session.commit()
    game.set_status('approved')

    players = [creator]

    # have all the other users play that game
    for user in users[1:]:
        players.append(join_game(game, user))

    session.add_all(players)
    session.commit()

    return game, users, players


def simulate_day(session, game, players):
    """
    Simulate players killing each other for a day.

    A day is a phase of the game where no respawns take place.
    """

    for player in players:
        assert player.alive
        assert len(player.contracts) == 1

    # Number of kills to simulate.
    kills = random.randint(1, len(players) - 1)

    print kills
    for _ in range(kills):
        contract = random.choice(game.contracts)
        print "Simulating completion of %s" % contract
        new_contracts = handle_kill(
            session, game, contract.killer, contract.target, contract)

    # At the end of the day, players are revived.
    assert kills == len([player for player in players if not player.alive])


def simulate_game(session, player_count, days=1):
    game, users, players = setup_everything(session, player_count)

    start_game(session, game)

    for _ in range(days):
        print "---- pre day %d ----" % _
        # Consistency check
        for player in players:
            assert player.alive
            assert len(player.contracts) == 1

        simulate_day(session, game, players)

        print "---- post day %d kills ----" % _
        # Consistency check
        for player in players:
            if player.alive:
                assert len(player.contracts) in [0, 1]

        resurrect_all(session, game)

        print "---- post day %d ----" % _
        # Consistency check
        for player in players:
            assert player.alive
            assert len(player.contracts) == 1
