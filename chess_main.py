#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 23:47:52 2021

@author: Zach
"""

import os
import sys

import pygame as p

import chess_engine


WIDTH = HEIGHT = 720                    # Width and height of board in pixels.
DIMENSION = 8                           # Chess board is 8 x 8 squares.
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 120                            # For animations later on.
IMAGES = {}                             # Setup for loadImages().
FLIPPEDBOARD = [i for i in reversed(range(DIMENSION))]  # For getting screen
    # coordinates when the board is drawn from Black's perspective.
THEMES = dict(
    # TODO:  Add more themes for custom board colors.
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
    squareClicked = ()  # No initial square selected, holds last square
        # clicked by user
    playerClicks = []  # Keep track of player clicks
        # (two tuples: [(4, 6), (4, 4)] would be (e2 pawn to) e4)
    gs.upside_down = False
    
    while True:
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
                if squareClicked == (file, rank):  # User clicked the same
                    # square twice.
                    deselectSquare(squares[file, rank])
                    squareClicked = ()
                    playerClicks = []  # Clear player clicks.
                else:
                    squareClicked = (file, rank)
                    playerClicks.append(squareClicked)  # Append for first
                    # and second click.

                # Stops move if first click is a blank square.
                if len(playerClicks) == 1:
                    if squares[playerClicks[0]].has_piece():
                        selectSquare(squares[playerClicks[0]], gs)
                    else:
                        squareClicked = ()
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
                                animateMove(validMove, screen, clock, gs, 
                                    theme, validMoves)
                                
                                moveMade = True
                                break
                        
                        if not moveMade:
                            deselectSquare(squares[playerClicks[0]])
                            if squares[playerClicks[1]].has_piece():
                                selectSquare(squares[playerClicks[1]], gs)
                                playerClicks = [playerClicks[1]]
                            
                            else:
                                squareClicked = ()
                                playerClicks = []
            
            # Key handlers
            elif event.type == p.KEYDOWN:
                # Undo move when CTRL+Z is pressed.
                if ((event.mod & p.KMOD_CTRL and event.key == p.K_z)
                    or event.key == p.K_LEFT
                    or event.key == p.K_a):
                    if len(gs.move_log) > 0:
                        gs.undo_move()
                        move = gs.undo_log.copy().pop()[0]
                        animateMove(move, screen, clock, gs, theme, 
                            validMoves, undo=True)
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
                    if len(gs.undo_log) > 0:
                        gs.redo_move()
                        move = gs.move_log.copy().pop()[0]
                        animateMove(move, screen, clock, gs, theme, validMoves)
                        moveMade = True
        
        if moveMade:
            validMoves = gs.get_valid_moves()
            moveMade = False
            if len(playerClicks) > 0:
                deselectSquare(squares[playerClicks[0]])
            squareClicked = ()
            playerClicks = []
        drawGameState(screen, gs, theme, validMoves)
        clock.tick(MAX_FPS)
        p.display.flip()


def loadImages():
    '''
    Initialize a global dictionary of images.

    This will be called exactly once in the main(), before the while: loop.
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


def drawGameState(screen, gs, theme, validMoves):
    '''
    Responsible for all the graphics within a current gamestate.
    '''
    # Draw squares on the board.
    drawBoard(screen, gs, theme, validMoves)
    # Highlight selected square and movement/capture squares.
    if selectedSquare != None:
        highlightSquares(selectedSquare, screen, gs, theme, validMoves)
    # Add in piece highlighting or move suggestions (later)
    drawPieces(screen, gs, theme)  # Draw pieces on the board.


def drawBoard(screen, gs, theme, validMoves):
    '''
    Draw the squares on the board.
    '''
    global selectedSquare
    selectedSquare = None
    squares = gs.board.squares.T.flat
    for square in squares:
        file, rank = square.get_coords()
        if gs.upside_down:
            file, rank =file, rank = FLIPPEDBOARD[file], FLIPPEDBOARD[rank]
        if square.is_selected():
            selectedSquare = square
        if square.get_color() == 'light':
            color = THEMES[theme][0]
        elif square.get_color() == 'dark':
            color = THEMES[theme][1]
                
        p.draw.rect(
            screen, color, p.Rect(
                file * SQ_SIZE, rank * SQ_SIZE,
                SQ_SIZE, SQ_SIZE,
            )
        )


def highlightSquares(selectedSquare, screen, gs, theme, validMoves):
    file, rank = selectedSquare.get_coords()
    if gs.upside_down:
        file, rank = FLIPPEDBOARD[file], FLIPPEDBOARD[rank]
    if selectedSquare.get_color() == 'light':
        color = THEMES[theme][2]
    elif selectedSquare.get_color() == 'dark':
        color = THEMES[theme][3]
    
    p.draw.rect(
        screen, color, p.Rect(
            file * SQ_SIZE, rank * SQ_SIZE,
            SQ_SIZE, SQ_SIZE,
        )
    )
    
    moveSquares, captureSquares = (
        markMovementSquares(selectedSquare, validMoves)
    )
    # Draw markers for move squares:
    if len(moveSquares) > 0:
        for square in moveSquares:
            file, rank = square.get_coords()
            if gs.upside_down:
                file, rank = FLIPPEDBOARD[file], FLIPPEDBOARD[rank]
            surface = p.Surface((SQ_SIZE, SQ_SIZE))
            surface.set_alpha(80)
            surface.fill(p.Color('green'))
            screen.blit(surface, (file * SQ_SIZE, rank * SQ_SIZE,))

    # Draw markers for capture squares.
    if len(captureSquares) > 0:
        for square in captureSquares:
            file, rank = square.get_coords()
            if gs.upside_down:
                file, rank = FLIPPEDBOARD[file], FLIPPEDBOARD[rank]
            attackSquare = p.Surface((SQ_SIZE, SQ_SIZE))
            attackSquare.fill((230, 118, 118))
            attackSquare.set_alpha(255)
            screen.blit(attackSquare, (file * SQ_SIZE, rank * SQ_SIZE,))
            # p.draw.circle(
            #     attackSquare,
            #     'red',
            #     (0.5*SQ_SIZE, 0.5*SQ_SIZE),
            #     SQ_SIZE // 2.1,
            #     6,
            # )


def drawPieces(screen, gs, theme):
    '''
    Draw the pieces on the board using the current GameState.board.
    '''
    pieces = gs.board.get_pieces()
    for piece in pieces:
        file, rank = piece.get_coords()
        if gs.upside_down:
            file, rank =file, rank = FLIPPEDBOARD[file], FLIPPEDBOARD[rank]
        pieceName = piece.get_image_name()
        screen.blit(
            IMAGES[pieceName], p.Rect(
                file * SQ_SIZE, rank * SQ_SIZE,
                SQ_SIZE, SQ_SIZE,
            )
        )


def markMovementSquares(square, validMoves):
    '''
    Finds the squares that the selected piece can move to and stores them as
    two lists.  
    
    These lists are used in the drawBoard function to highlight move and 
    capture squares of the selected piece.
    '''
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


def animateMove(move, screen, clock, gs, theme, validMoves, undo=False):
    '''Animates pieces when they are moved.'''
    # Get move info.
    pieceMoved = move.piece_moved
    pieceCaptured = move.piece_captured
    startSquare, endSquare = move.start_square, move.end_square
    if undo:
        startSquare, endSquare = endSquare, startSquare
        pieceCaptured = None
    startFile, startRank = startSquare.get_coords()
    endFile, endRank = endSquare.get_coords()
    endSquareColor = endSquare.get_color()
    dFile = endFile - startFile  # Change in file for the piece moved.
    dRank = endRank - startRank  # Change in rank for the piece moved.
    if move.contains_castle():
        rook, rookStartSquare, rookEndSquare = move.castle
        if undo:
            rookStartSquare, rookEndSquare = rookEndSquare, rookStartSquare
        rookStartFile, rookStartRank = rookStartSquare.get_coords()
        rookEndFile, rookEndRank = rookEndSquare.get_coords()
        dRookFile = rookEndFile - rookStartFile
        dRookRank = rookEndRank - rookStartRank
        rookEndSquareColor = rookEndSquare.get_color()
    framesPerMove = MAX_FPS // 10 + 1  # Number of frames to one move.
    # moveDistance = abs(dRank) + abs(dFile)
    for frame in range(1, framesPerMove):
        drawBoard(screen, gs, theme, validMoves)
        drawPieces(screen, gs, theme)
        # Erase the piece being moved from its ending square.
        if endSquareColor == 'light':
            color = THEMES[theme][0]
        elif endSquareColor == 'dark':
            color = THEMES[theme][1]
        p.draw.rect(screen, color,
            p.Rect(endFile*SQ_SIZE, endRank*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        if move.contains_castle():
            if rookEndSquareColor == 'light':
                color = THEMES[theme][0]
            elif rookEndSquareColor == 'dark':
                color = THEMES[theme][1]
            p.draw.rect(screen, color,
                p.Rect(rookEndFile*SQ_SIZE, rookEndRank*SQ_SIZE,
                    SQ_SIZE, SQ_SIZE))
            drawAnimationFrame(rook, None, rookStartFile, rookStartRank, 
                dRookFile, dRookRank, rookEndFile, rookEndRank, frame,
                framesPerMove, screen)
        drawAnimationFrame(pieceMoved, pieceCaptured, startFile, startRank, 
            dFile, dRank, endFile, endRank, frame, framesPerMove, screen)
        
        p.display.flip()
        clock.tick(MAX_FPS)


def drawAnimationFrame(pieceMoved, pieceCaptured, startFile, startRank, dFile,
    dRank, endFile, endRank, frame, framesPerMove, screen):
    '''
    Draws a single frame of animation.
    '''
    file, rank = (startFile + dFile*frame/framesPerMove, 
                  startRank + dRank*frame/framesPerMove)
    # Draw captured piece onto end Square.
    if pieceCaptured != None:
        screen.blit(IMAGES[pieceCaptured.get_image_name()], 
            p.Rect(endFile*SQ_SIZE, endRank*SQ_SIZE, SQ_SIZE, SQ_SIZE))
    # Draw moving piece.
    screen.blit(IMAGES[pieceMoved.get_image_name()], 
        p.Rect(file*SQ_SIZE, rank*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        


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
    '''Deselects a selected square.'''
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
        promoteMenu(gs, move)


def exitGame():
    p.quit()
    sys.exit()





if __name__ == '__main__':
    main()





