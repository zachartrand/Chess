# Object-oriented chess engine

<img src='images/screenshot.png' width="70%" alt='Chess Program Screenshot'>

## Downloads

### The game

You can download the latest release here:  [Latest release](https://github.com/zachartrand/Chess/releases)

You can also clone the repository with the following terminal command:

```bash
$ git clone https://github.com/zachartrand/Chess.git
```

### Dependencies

#### Python

Download the latest version here:  [Download Python](https://www.python.org/downloads/)

#### Pygame

Instructions to download Pygame are here:  [Pygame: Getting Started](https://www.pygame.org/wiki/GettingStarted)

#### NumPy

Instructions to download NumPy are here: [Installing NumPy](https://numpy.org/install/)

## How to run

This game uses [Python 3.8](https://www.python.org/downloads/release/python-3811/),
[Pygame 2.0](https://www.pygame.org/wiki/GettingStarted), and [NumPy 1.20](https://numpy.org/install/).
When testing, the main was called in the [IPython](https://ipython.org/) terminal,
so that might be the best console to use when running this game.
To run, open the chess_main.py file using Python or IPython in a command
prompt window. If your Python distribution is through conda, be sure to
have your conda environment activated before trying to load the main file.

```bash
$ ipython chess_main.py
```

## About
This game was designed for me to learn object oriented programming.  Since I 
know the rules to Chess, I figured I could build objects based on aspects of 
the game and make a working game from those objects.  I'm not sure if this is 
the most efficient way to make the game, but that isn't really the point of 
this exercise.

The chess_engine and chess_main were made following the YouTube tutorial by Eddie 
Sharick, found here:

- [Chess Engine in Python](https://youtu.be/EnYui0e73Rs&list=PLBwF487qi8MGU81nDGaeNE1EnNEPYWKY_)
    
and then modified to work with the objects that I created.  Unlike Eddie's program, 
this one uses objects as the pieces and board elements whereas his pieces and board 
are text and a list of lists, respectively. I have also cleaned up some of the 
algorithms used to find squares for the pieces to move to and added square highlighting
when pieces are selected.
