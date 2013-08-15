Bloodtide
=========

There are lots of versions of bloodtide. Only one of them was ever in a consistent state.

The first one, my initial attempt, got bogged down by bad style and organization and was "refactored" (rewritten) to the second attempt, but that never was fully completed, leaving that attempt in an incosistent state. Things have since gotten worse.

My method in the past has been to do an additive approach, where I take piece by piece from old attempts, adding them to the new one. It hasn't worked, maybe from lack of dedicacion, maybe from not having functional goals to take me from one addition to the next.

What would be a better approach?

I can't imagine a subtractive approach, really.

Doing It?
---------

### Step One: A functional anything.

I need a basic amount of functionality. I need something that I can run and say "this does such and such, and it does it correctly." This won't involve the web interface at all. It is probably a simulation of the game I am looking for.

This means the models and the core gameplay code. The main work I need to do is creating the simulation code, really.

So maybe that is where I should start.

Then add more gameplay code, link up half user sign up and make sure it all works.

The goal milestone is "Playable". This has been achived when I can tell a bunch of friends how to join a game I made and play it out.

So Many Repos
-------------

assassin

    the original, sorta poor code, but probably the most of it

temp_assassin

    some web stuff, pulling stuff in from assassin at least, maybe based off of a different version... hard to tell.

Yet Another Attempt
-------------------

So I will probably have to start over, yet again. I can take the good models.py file from wherever, then go over the models, especially user, and make sure it is properly written. I should probably have a specification as well. Maybe not, wahtevs.

I can probably straight up steal the utility stuff (though with changes to how  kill codes are stored/gened).

Then I need to create a plan to make a game simulation.

Models look as good as ever. What to add next? I need to start to get the game play logic in place. I don't actually have to worry about flask, I don't think. I mean, simulating a game doesn't really require the flask stuff layed over the rest of the code. I do need to get the sqlalchemy data base in place...

Speaking of Alchemy
-------------------

I need to pick a method and take it to the extreme (I walk a mic like a vandal). I like the "move the database handle upwards" and have every methods that really needs it take a 'db' argument. Everything that can should just take data (unittestable!).

Milestone: simulation Plan
--------------------------

I have the models, now I need to simulate them. What do I need to do that?

I should just start with a big 'game.py' file that does all the game logic. This can be refactored as needed. What functions do I need to run the game?

    explicit changes

        init the game with these players
        player a kills player b
        player is revived

Anyway, the top level api would be something like

    All of these functions should operate on game level objects. They don't send texts, talk to players, have a database handle: none of that shit. They simply take some data and transform it. The code will be run against a test sql database, so the full sql alchemy ORM interface can be used.

    They should all be building block level functions that can be composed into higher level logic. Ex, having a player kill their target then get a new contract should be two seperate functions.

    init_game(game)

        assign all the players their initial contracts

    kill_player(killer, target, contract)

        Player |killer| kills Player |target|. Doesn't look up target by kill code or anything, simply ends

    revive_player(player)

        bring Player |player| back to life. Does not assign a new contract.

    new_contract(player)

        create a new contract for Player |player|.

I am actually going to simplify the game a little by ignoring contract expiration dates. They are valid until a kill is stolen or the holder dies. This takes out all time based aspects and lets me concentrate solely on players influence over the game state.

Next Lowest Level
-----------------

Okay, a basic game.py is done. What else do I need to reach simulation?

Well, I need to create a test game, and have test users join it. Creating test users should be a test fixture. Making players for them should not. I also need to be able to create a game.

So that is it really,

    create_game(admin)

    join_game(user)

    start_game()

        calls init_game? are they the same? This should probably be a level higher.

So now that I have these, I need to write some tests. Let's start this by... Well, I need to create fake users. Also, there are going to be two types of tests (in addition to unit tests, I guess). Anyway...

    localish tests, where I test only one or two functions...

    and end to end tests, where I simulate a full game, asserting invarients the whole time.

Either way, I need some test fixtures. I need to be able to create a bunch of fake users. One needs to be an admin. Then have the admin join a game, and all of the users do so as well.

I might be able to just never commit a session in the smaller tests... just add a bunch of users to a session, giving them IDs and such if needed (or flushing the session?.. but that would probably require a DB... maybe I should just use a db...). Anyway, I need a test db, that is for sure. It can get wiped all the time, wahtevs, it just needs to host one test at a time.


Invariants
----------

A dead player should
    have no open contracts
    be never be the target of an open contract

A player can never be his own target.

A (open) contract can never be held by a dead player.
A (open) contract can never target a dead player.

A player can have at most one open contract targeting another player.

Hic Up
------

Currently, all the models try to do `from bloodtide import db`, which isn't going to work, for two reasons. a) I don't even have that file really and b) if I did it wouldn't have the correct config for tests. So I think I need to define it in like, a special db file that lives by the models, db.py, that has the db definition. It should have a way to know if it is being setup as a test or not though, so that I don't fff up the actual DB. Hmm.

I think I want it so that I can hit 'nosetests' whenever and it will work, even for DB tests. Actually, I don't know if I will use nosetests for non-unittests. I don't want the DB code run every time I want to run the unittest suite. None the less, I want to be able to 'just run the tests' without having to change environment variable and such. I can just add a block of code to the top of the simulation test or whatever that either changes os.env (or wahtev) or changes something in the db file to work.

Simulation
----------

I think I am close to or done with the simulation milestone. I can simulate 10 users in a game playing for 10 days, and everything appears to be correct. Actually, maybe I should add a new milestone before Playeable called Advanced Simulation that covers important things like assignment of new contracts in a better way.

Advanced Simulation
-------------------

expire contracts?

    really important for the actual game

multiple contracts

    less important for the actual game (at first) but will put some pressure on the apis of game and base_game, so I should address it now.

better assignment of contracts, match making and scoring

    we want to bring the number of stolen contracts down and make the game more weighted towards good players targeting good players

recognize killing sprees?

    goes with above, being on a killing spree makes you worth more

more fine grained control over the simulations

    things like player aggressiveness, involvement, and such. this could be stated as 'simulation towards design' instead of correctness. I don't just want code coverage, I want to see how game rules effect different types of players and player type composition.

    * player type composition (skilled, unskilled, undedicatded, etc)

    and simulation reports/summaries

assignment grouping

    if only a small amount of time is left before the new assignment period, hold of creating new contracts so that we can more intelligently give out contracts.

this milestone will require a significant amount of design, especially the match making side of things.

I should get this shit up in a private repo on github.
