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
MAX_FPS = 60                            # For animations later on.
IMAGES = {}                             # Setup for loadImages().
FLIPPEDBOARD = [i for i in reversed(range(DIMENSION))]  # For getting screen
    # coordinates when the board is drawn from Black's perspective.
THEMES = dict(
        # TODO:  Make dictionary of different themes for custom board colors.
        blue = (
            p.Color(214, 221, 229),  # light square
            p.Color(82, 133, 180),   # dark square
            p.Color(253, 187, 115),  # light square highlight
            p.Color(255, 129, 45),   # dark square highlight
            p.Color(148, 206, 159),  # light move square
            p.Color(54, 170, 124),   # dark move square
        ),
        bw = (
            p.Color(255, 255, 255),  # light square
            p.Color(100, 100, 100),  # dark square
            p.Color(140, 236, 146),  # light square highlight
            p.Color(30, 183, 37),    # dark square highlight
            p.Color(148, 206, 159),  # light move square
            p.Color(54, 170, 124),   # dark move square
        ),
        yellow = (
            p.Color(247, 241, 142),  # light square
            p.Color(244, 215, 4),    # dark square
            p.Color(253, 187, 115),  # light square highlight
            p.Color(255, 129, 45),   # dark square highlight
            p.Color(148, 206, 159),  # light move square
            p.Color(54, 170, 124),   # dark move square
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
    gs.upside_down = False
    
    while True:
        if len(validMoves) == 0:
            if gs.in_check:
                print('Checkmate')
            else:
                print('Stalemate: No valid moves.')
            
            if (input('Would you like to quit the game?').lower() == 'y'):
                exitGame()
            else:
                gs.undo_move()
                moveMade = True
        # Event handler.  Manages inputs like mouse clicks and button presses.
        for event in p.event.get():
            # Allows the game to be closed.
            if event.type == p.QUIT:
                exitGame()
            
            # Mouse handlers
            elif event.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # (x, y) location of the mouse.
                file = location[0] // SQ_SIZE
                rank = location[1] // SQ_SIZE
                if gs.upside_down:
                    file, rank = FLIPPEDBOARD[file], FLIPPEDBOARD[rank]
                if squareSelected == (file, rank):  # User clicked the same 
                    # square twice.
                    deselectSquare(squares[file, rank])
                    squareSelected = ()
                    playerClicks = []  # Clear player clicks.
                else:
                    squareSelected = (file, rank)
                    playerClicks.append(squareSelected)  # Append for first 
                    # and second click.
                
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
                        for validMove in validMoves:
                            if move == validMove:
                                pieceMoved = validMove.piece_moved
                                if (pieceMoved.get_name() == 'Pawn'
                                    and pieceMoved.can_promote()):
                                    promoteMenu(gs, validMove)
                                gs.make_new_move(validMove)
                                
                                moveMade = True
                                break
                                
                        if not moveMade:
                            deselectSquare(squares[playerClicks[0]])
                            if squares[playerClicks[1]].has_piece():
                                selectSquare(squares[playerClicks[1]], gs)
                                playerClicks = [playerClicks[1]]
                            
                            else:
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
            if len(playerClicks) > 0:
                deselectSquare(squares[playerClicks[0]])
            squareSelected = ()
            playerClicks = []
        drawGameState(screen, gs, theme)
        clock.tick(MAX_FPS)
        p.display.flip()
        

def drawGameState(screen, gs, theme):
    '''
    Responsible for all the graphics within a current gamestate.
    '''
    drawBoard(screen, gs, theme)  # Draw squares on the board.
    # Add in piece highlighting or move suggestions (later)
    drawPieces(screen, gs, theme)  # Draw pieces on the board.
    


def drawBoard(screen, gs, theme):
    '''
    Draw the squares on the board.
    '''
    squares = gs.board.squares.T.flat
    moveSquares = []
    captureSquares = []
    for square in squares:
        file, rank = square.get_coords()
        if gs.upside_down:
            file, rank =file, rank = FLIPPEDBOARD[file], FLIPPEDBOARD[rank]
        if square.is_selected():
            moveSquares, captureSquares = markMovementSquares(square, gs)
        if square.get_color() == 'light':
            color = THEMES[theme][0]
        elif square.get_color() == 'dark':
            color = THEMES[theme][1]
        
        p.draw.rect(screen, color, p.Rect(
        file * SQ_SIZE, rank * SQ_SIZE,
        SQ_SIZE, SQ_SIZE,
        ))
        
     # Draw markers for move squares:
    if len(moveSquares) > 0:
        for square in moveSquares:
            file, rank = square.get_coords()
            if gs.upside_down:
                file, rank = FLIPPEDBOARD[file], FLIPPEDBOARD[rank]
            if square.get_color() == 'light':
                color = THEMES[theme][4]
            elif square.get_color() == 'dark':
                color = THEMES[theme][5]
            p.draw.rect(screen, color, p.Rect(
            file * SQ_SIZE, rank * SQ_SIZE,
            SQ_SIZE, SQ_SIZE,
            ))
            
    if len(captureSquares) > 0:
        for square in captureSquares:
            color = (230, 118, 118, 0)
            file, rank = square.get_coords()
            if gs.upside_down:
                file, rank = FLIPPEDBOARD[file], FLIPPEDBOARD[rank]
            p.draw.rect(screen, color, p.Rect(
            file * SQ_SIZE, rank * SQ_SIZE,
            SQ_SIZE, SQ_SIZE,
            ))
            # p.draw.circle(
            #     screen,
            #     color,
            #     ((file + 0.5) * SQ_SIZE, (rank + 0.5) * SQ_SIZE),
            #     SQ_SIZE // 2.1,
            #     6,
            # )
        
    


def drawPieces(screen, gs, theme):
    '''
    Draw the pieces on the board using the current GameState.board.
    '''
    
    pieces = gs.board.get_pieces()
    for piece in pieces:
        square = piece.get_square()
        file, rank = square.get_coords()
        if gs.upside_down:
            file, rank =file, rank = FLIPPEDBOARD[file], FLIPPEDBOARD[rank]
        if square.is_selected():
            if square.get_color() == 'light':
                color = THEMES[theme][2]
            elif square.get_color() == 'dark':
                color = THEMES[theme][3]
            
            p.draw.rect(screen, color, p.Rect(
            file * SQ_SIZE, rank * SQ_SIZE, 
            SQ_SIZE, SQ_SIZE,
            ))
        pieceName = piece.get_image_name()
        screen.blit(
            IMAGES[pieceName], p.Rect(
                file * SQ_SIZE, rank * SQ_SIZE,
                SQ_SIZE, SQ_SIZE,
            )
        )
        

def markMovementSquares(square, gs):
    validMoves = gs.get_valid_moves()
    moveSquares = []
    captureSquares = []
    for move in validMoves:
        if square == move.start_square:
            if (move.piece_captured != None
                or move.contains_enpassant()):
                captureSquares.append(move.end_square)
            else:
                moveSquares.append(move.end_square)
                
    return moveSquares, captureSquares

        
def selectSquare(square, gs):
    '''
    Adds a flag to highlight the square that is clicked on if the piece 
    color is the same as the turn.
    '''
    if not square.is_selected():
        color = square.get_piece().get_color()
        if ((color == 'white' and gs.white_to_move)
            or (color == 'black' and not gs.white_to_move)):
            square.selected = True


def deselectSquare(square):
    if square.is_selected():
        square.selected = False
    

def promoteMenu(gs, move):
    choices = 'qkrb'
    print('What would you like to promote your Pawn to?')
    i = input('q = Queen, k = Knight, b = Bishop, r = Rook\n')
    if i[0].lower() in choices:
        gs.promote(i[0], move)
    else:
        print('Incorrect choice.')
        promoteMenu(move.piece_moved)
    
    
def exitGame():
    p.quit()
    sys.exit()
    
    

# =============================================================================
# Older functions for drawing the squares on the board.
# 
# def drawBoard2(screen, board, theme):
#     '''
#     Draw the squares on the board.
#     '''
#     for rank in range(DIMENSION):
#         for file in range(DIMENSION):
#             if (board.squares[file, rank].get_color() == 'light'):
#                 if board.squares[file, rank].is_selected():
#                     color = THEMES[theme][2]
#                 else:
#                     color = THEMES[theme][0]
#             else:
#                 if board.squares[file, rank].is_selected():
#                     color = THEMES[theme][3]
#                 else:
#                     color = THEMES[theme][1]
#             p.draw.rect(screen, color, p.Rect(
#                 file * SQ_SIZE, rank * SQ_SIZE, SQ_SIZE, SQ_SIZE,
#                 ))
#             
# def drawBoard3(screen, board, theme):
#     '''
#     Draw the squares on the board.
#     '''
#     squares = board.squares.T.flat
#     for square in squares:
#         file, rank = square.get_coords()
#         if square.get_color() == 'light':
#                 if board.squares[file, rank].is_selected():
#                     color = THEMES[theme][2]
#                 else:
#                     color = THEMES[theme][0]
#         else:
#             if square.is_selected():
#                 color = THEMES[theme][3]
#             else:
#                 color = THEMES[theme][1]
#         p.draw.rect(screen, color, p.Rect(
#             file * SQ_SIZE, rank * SQ_SIZE,
#             SQ_SIZE, SQ_SIZE,
#             ))
# =============================================================================

    




if __name__ == '__main__':
    main()









