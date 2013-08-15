"""
Low level interface to manipulate a game of bloodtide.
"""

import random

from bloodtide.models import Contract


def init_game(game):
    """
    Give all players in Game |game| a starting contract, mark all
    players as alive.

    Returns initial contracts.
    """

    assert game.status == 'approved'
    game.set_status('active')

    for player in game.players:
        # TODO: Actually create life ids...
        player.resurrect(str(random.randint(100000, 999999)))

    print('%s initialized.' % game)

    return seed_contracts(game.players)


def kill_player(killer, target, contract):
    """
    End Contract |contract| between Player |killer| and Player |target|
    also ending all of |target|'s contracts and marking any contracts
    as stolen. Does not create a new contract for |killer|.

    Return all stolen contracts after concluding them.
    """

    target.kill()
    contract.conclude('completed')
    stolen_contracts = []

    print('%s kills %s' % (killer, target))
    print('\t%s completed' % contract)

    for targets_contract in target.contracts:
        targets_contract.conclude('uncompleted')
        print('\t%s uncompleted' % targets_contract)

    for target_of_contract in target.target_of_contracts:
        stolen_contracts.append(target_of_contract)
        target_of_contract.conclude('stolen')
        print('\t%s stolen from %s' % (
            target_of_contract, target_of_contract.killer))

    return stolen_contracts


def resurrect_player(player):
    """
    Bring Player |player| back to life. Does not assign a new contract.
    """

    assert player.alive is False

    # TODO: Actually generate life ids...
    player.resurrect(str(random.randint(100000, 999999)))
    print('%s resurrected' % player)


def new_contract(game, player):
    """
    Create a new contract for Player |player|. Target will be chosen
    from the alive players in |game| intelligently*.

    Return the new contract, or None if no valid contract could be
    created.

    * not really, not yet at least.
    """

    current_target_ids = [t.id for t in player.targets]

    def target_of(target):
        return len(target.target_of_contracts)

    def valid_target(target):
        if target.alive and target.id != player.id:
            if not target.id in current_target_ids:
                return True

    options = filter(valid_target, sorted(game.players, key=target_of))

    if not options:
        return None

    contract = Contract(player, options[0])
    print('new contract %s' % contract)
    print('\t%s targetting %s' % (player, options[0]))

    return contract


def seed_contracts(players, contract_count=1):
    """
    Assign |contract_count| initial contracts to all Players in
    |players|.

    Retrun a list of new contracts between |players| such that every
    player targets |contract_count| other unique players.
    """

    assert contract_count in range(1, len(players))

    count = len(players)
    ids = range(count)
    contracts = []

    random.shuffle(ids)

    for ndx in range(count):
        player = players[ids[ndx % count]]
        for i in range(contract_count):
            target = players[ids[(ndx + i + 1) % count]]
            contracts.append(Contract(player, target))

    print('%d contracts seeded' % len(contracts))

    return contracts
