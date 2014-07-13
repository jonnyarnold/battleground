Battleground
============

Customisable turn-based strategy game for two players.

WTF?
====

Battleground pits two factions against each other. The objective is simple: eliminate all of the opposing units.

The Battleground
----------------

Each side has a front and back area, with a certain number of spaces for units. Units join the game from the back, but cannot attack until they are moved to the front. Units at the back recover some of their Hits per turn, up to their initial number of Hits (see Units below). Units at the front can attack and can be attacked by the opposition.

Points
------

All actions in Battleground cost points. The current number of points you have is shown at the bottom of the screen. You receive points at the start of every turn and can spend points during your turn to create units, move units and attack.

Units
-----

Each unit has a numeric skill level for each of the following skills:
* Hits: The amount of damage that can be sustained by the unit before it is removed from play. This is also the maximum amount of Hits that can be regenerated whilst in the back area.
* Attack/Defense: Used to calculate the amount of damage a hit will cause.
* Accuracy/Speed: Used to calculate the chance of hitting a unit.
* Enlist Cost: The number of points required to create this unit.
* Action Cost: The number of points required to move or attack with this unit.

Playing the Game
----------------

On your turn you can do as many of the following as you wish (provided you have the points and spaces to do so):
* Create a unit. To do this, select an empty space and select Add Unit. A screen will appear detailing all of the units at your disposal.
* Move a unit (from the front to the back, or vice versa). A unit can only be moved once per turn. To do this, select a unit and select 'Move to Front' or 'Move to Back'.
* Attack the opposition! A unit can only attack once per turn. To do this, select a unit at the front and select Attack. The screen will highlight the enemy side: select a target. Once a target has been selected, a fight summary will appear showing the likelihood and damage given for the fight.

To end your turn, select End Turn.

Important Rules
---------------
* Units receive a bonus or penalty depending on their success during a fight.
* If a side has no units in the front area the player can attack units in the back area. Units being attacked in the back area suffer a penalty on all of their skills.

Customising the Game
====================

The sides and art are customisable.
* The `sides` folder provides a way of specifying the skill levels and art for each unit. Note that the Enlist Cost and Action Cost are calculated automatically based on the skill levels provided.

Techincal Details
=================

The game is written in Python using the [PyGame](http://www.pygame.org/) library. The game also uses [GTK](http://www.gtk.org/) for a cross-platform GUI, together with [Glade](https://glade.gnome.org/) to build them quickly. Ubuntu users will want the packages `python-pygame` and `python-glade2`.
