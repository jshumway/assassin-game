"""
Useful functions for testing bloodtide.
"""

import random

from bloodtide.models import User

# Test data.
fnames = [
    "Adam",
    "Alex",
    "Alice",
    "Amber",
    "Brent",
    "Bob",
    "Ellie",
    "John",
    "Josh",
    "Tyler",
    "Vanessa",
]

lnames = [initial + '.' for initial in "abcdefghijklmnopqrstuvwxyz".upper()]

def create_users(count, full=True):
    """
    Create |count| users. If |full| is True, the first user created
    will be a full user. All other users will be half users.

    Return the list of created users.
    """

    assert count > 0

    users = []

    for ndx in range(count):
        make_full = ndx == 0 and full
        users.append(User(
            ''.join([str(random.randint(0, 10)) for _ in range(11)]),
            random.choice(fnames),
            random.choice(lnames),
            'full' if make_full else 'half',
            password='canihaveroot' if make_full else None))

    return users
