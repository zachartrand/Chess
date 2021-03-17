# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 23:47:52 2021

@author: Zach
"""

import os
import sys

import pygame as p

import chess_engine


WIDTH = HEIGHT = 768                    # Width and height of board in pixels.
DIMENSION = 8                           # Chess board is 8 x 8 squares.
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 24                            # For animations later on.
IMAGES = {}                             # Setup for loadImages().
THEMES = dict(
        # TODO:  Make dictionary of different themes for custom board colors.
        blue = (
            p.Color(214, 221, 229),  # light square
            p.Color(82, 133, 180),   # dark square
            p.Color(253, 187, 115),  # light square highlight
            p.Color(255, 129, 45),   # dark square highlight
        ),
        bw = (
            p.Color(255, 255, 255),  # light square
            p.Color(100, 100, 100),  # dark square
            
            p.Color(140, 236, 146),  # light square highlight
            p.Color(30, 183, 37),    # dark square highlight
        ),
        yellow = (
            p.Color(247, 241, 142),  # light square
            p.Color(244, 215, 4),    # dark square
            p.Color(253, 187, 115),  # light square highlight
            p.Color(255, 129, 45),   # dark square highlight
        ),
    )

def loadImages():
    '''
    Initialize a global dictionary of images. 
    
    This will be called exactly once in the main().
    '''
    colors = ['w', 'b']
    pieces = ['K', 'Q', 'R', 'B', 'N', 'P']
    for color in colors:
        for piece in pieces:
            pieceName = ''.join([color, piece])
            IMAGES[pieceName] = p.transform.smoothscale(
                p.image.load(os.path.join('images', pieceName + '.png')),
                (SQ_SIZE, SQ_SIZE),
            )
    

def main():
    '''
    The main driver for our code. 
    
    This will handle user input and updating the graphics.
    '''
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color(28, 28, 28))
    theme = 'blue'
    gs = chess_engine.GameState()
    board = gs.board
    squares = board.squares
    validMoves = gs.get_valid_moves()
    moveMade = False  # Flag variable for when a move is made. Prevents engine
        # from wasting resources every frame to find all valid moves.
    
    loadImages()  # Only do this once, before the while loop.
    squareSelected = ()  # No initial square selected, holds last square 
        # clicked by user
    playerClicks = []  # Keep track of player clicks 
        # (two tuples: [(4, 6), (4, 4)] would be (e2 pawn to) e4)
    
    while True:
        if len(validMoves) == 0:
            print('Checkmate')
        # Event handler.  Manages inputs like mouse clicks and button presses.
        for event in p.event.get():
            # Allows the game to be closed.
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            
            # Mouse handlers
            elif event.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # (x, y) location of the mouse.
                file = location[0] // SQ_SIZE
                rank = location[1] // SQ_SIZE
                if squareSelected == (file, rank):  # User clicked the same 
                    # square twice.
                    squares[squareSelected].selected = False
                    squareSelected = ()
                    playerClicks = []  # Clear player clicks.
                else:
                    squareSelected = (file, rank)
                    playerClicks.append(squareSelected)  # Append for first and
                        # second click.
                
                # Stops move if first click is a blank square.
                if len(playerClicks) == 1:
                    if squares[playerClicks[0]].has_piece():
                        selectSquare(squares[playerClicks[0]], gs)
                    else:
                        squareSelected = ()
                        playerClicks = []
                
                if len(playerClicks) == 2:  # After second click.
                    # Only register a move if the first 
                    # square clicked has a piece.
                    if squares[playerClicks[0]].has_piece():
                        move = chess_engine.Move(
                            squares[playerClicks[0]],
                            squares[playerClicks[1]],
                            gs.move_number
                        )
                        if move in validMoves:
                            gs.make_new_move(move)
                            moveMade = True
                            squares[playerClicks[0]].selected = False
                            squareSelected = ()
                            playerClicks = []
                        else:
                            if squares[playerClicks[1]].has_piece():
                                squares[playerClicks[0]].selected = False
                                selectSquare(squares[playerClicks[1]], gs)
                                playerClicks = [playerClicks[1]]
                            
                            else:
                                squares[playerClicks[0]].selected = False
                                squareSelected = ()
                                playerClicks = []
            
            # Key handlers        
            elif event.type == p.KEYDOWN:
                # Undo move when CTRL+Z is pressed.
                if ((event.mod & p.KMOD_CTRL and event.key == p.K_z)
                    or event.key == p.K_LEFT
                    or event.key == p.K_a):
                    gs.undo_move()
                    moveMade = True
                # Redo move when CTRL+R is pressed.
                if (
                       (   
                           event.mod & p.KMOD_CTRL and (
                               event.key == p.K_r or event.key == p.K_y
                           )
                    ) or event.key == p.K_RIGHT 
                    or event.key == p.K_d
                ):  
                    gs.redo_move()
                    moveMade = True
                    
        
        if moveMade:
            validMoves = gs.get_valid_moves()
            moveMade = False
        drawGameState(screen, gs, theme)
        clock.tick(MAX_FPS)
        p.display.flip()
        

def drawGameState(screen, gs, theme):
    '''
    Responsible for all the graphics within a current gamestate.
    '''
    drawBoard(screen, gs.board, theme)  # Draw squares on the board.
    # Add in piece highlighting or move suggestions (later)
    drawPieces(screen, gs.board)  # Draw pieces on the board.
    

def drawBoard(screen, board, theme):
    '''
    Draw the squares on the board.
    '''
    for rank in range(DIMENSION):
        for file in range(DIMENSION):
            if (board.squares[file, rank].get_color() == 'light'):
                if board.squares[file, rank].selected:
                    color = THEMES[theme][2]
                else:
                    color = THEMES[theme][0]
            else:
                if board.squares[file, rank].selected:
                    color = THEMES[theme][3]
                else:
                    color = THEMES[theme][1]
            p.draw.rect(screen, color, p.Rect(
                file * SQ_SIZE, rank * SQ_SIZE, SQ_SIZE, SQ_SIZE,
                ))


def drawPieces(screen, board):
    '''
    Draw the pieces on the board using the current GameState.board.
    '''
    pieces = board.get_pieces()
    for piece in pieces:
        file, rank = piece.get_coords()
        pieceName = piece.get_image_name()
        screen.blit(
            IMAGES[pieceName], p.Rect(
                file * SQ_SIZE, rank * SQ_SIZE, SQ_SIZE, SQ_SIZE,
            )
        )
        
def selectSquare(square, gs):
    color = square.get_piece().get_color()
    if ((color == 'white' and gs.white_to_move)
        or (color == 'black' and not gs.white_to_move)):
        square.selected = True
    
            
# =============================================================================
# def drawBoardUpsideDown(screen, board, theme):
#     '''
#     Draws the board from Black's perspective.
#     '''
#     fileNumber = rankNumber = [i for i in reversed(range(DIMENSION))]
#     
#     for f in range(DIMENSION):
#         for r in range(DIMENSION):
#             if (board.squares[fileNumber[f], rankNumber[r]].get_color() 
#                 == 'light'):
#                 color = THEMES[theme][0]
#             else:
#                 color = THEMES[theme][1]
#             p.draw.rect(screen, color, p.Rect(
#                 f * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE,
#                 ))
# =============================================================================
    

    




if __name__ == '__main__':
    main()














