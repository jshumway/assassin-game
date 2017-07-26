# bloodtide-game

Assassin game as a service using Twilio for text messaging.

Written back before it was safe to assume everyone had a smartphone.

A proof of concept written over Winter break. Most work went into the database modeling aspect of the project.

## Structure

An admin can create a game which players can join by texting a Twilio phone number with the entry code.

When the admin starts the game, the server assigns each player a secret code. When the player is 'assassinated' (squirt gun, tag, whatever rules are being used), the assassinated player given the assassinating player their code. The kill is verified with the server (simply text in the code), and the server assigns a new target. The assassinated player can also be given a new target, optionally removing the 'permadeath' aspect of the game.

## Status

I last worked on this project many years ago, and much has changed. If I created in today, I would do some things differently

* No need to rely on a service like Twilio, use a mobile first web app instead
* Streamline the sign up and 'verify assassination' steps
