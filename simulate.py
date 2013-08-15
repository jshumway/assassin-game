#!/usr/bin/env python

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bloodtide.models import Base
from tests.simulation import simulate_game


def run_simulation():
    engine = create_engine(os.environ['TEST_DATABASE_URL'])

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)

    simulate_game(Session(), 10, 10)


if __name__ == '__main__':
    run_simulation()
