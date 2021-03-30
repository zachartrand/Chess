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
# from chess_pieces import DIRECTIONS
import chess_ai as ai


CAPTION = 'Chess'
WIDTH = HEIGHT = 720                    # Width and height of board in pixels.
DIMENSION = 8                           # Chess board is 8 x 8 squares.
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 120                           # For animations later on.
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
    global screen, clock, theme, gs
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption(CAPTION)
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
    humanWhite = False  # True if human player is white.
    humanBlack = True  # True if human player is black.
    if humanBlack and not humanWhite:
        gs.upside_down = True
    
    while True:
        humanTurn = ((gs.white_to_move and humanWhite)
                      or (not gs.white_to_move and humanBlack))
        # Event handler.  Manages inputs like mouse clicks and button presses.
        for event in p.event.get():
            # Allows the game to be closed.
            if event.type == p.QUIT:
                exitGame()

            # Mouse handlers
            elif event.type == p.MOUSEBUTTONDOWN:
                if not gs.gameover and humanTurn:
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
                            selectSquare(squares[playerClicks[0]])
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
                                        promoteMenu(validMove)
                                    gs.make_new_move(validMove)
                                    animateMove(validMove, validMoves)
                                    # For debugging.
                                    print(validMove.get_chess_notation(), end=' ')
                                    moveMade = True
                                    break
                            
                            if not moveMade:
                                deselectSquare(squares[playerClicks[0]])
                                if squares[playerClicks[1]].has_piece():
                                    selectSquare(squares[playerClicks[1]])
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
                        animateMove(move, validMoves, undo=True)
                        # For debugging.
                        print('Undid {}'.format(move.get_chess_notation()), end=' ')
                        moveMade = True
                # Redo move when CTRL+R is pressed.
                if (
                        (event.mod & p.KMOD_CTRL and event.key == p.K_y) 
                         or event.key == p.K_RIGHT
                         or event.key == p.K_d
                ):
                    if len(gs.undo_log) > 0:
                        gs.redo_move()
                        move = gs.move_log.copy().pop()[0]
                        animateMove(move, validMoves)
                        # For debugging.
                        print('Redid {}'.format(move.get_chess_notation()), end='')
                        moveMade = True
        
        # AI move finder
        if (not gs.gameover and not humanTurn 
                and len(gs.undo_log) == 0 and not moveMade):
            AIMove = ai.getBestMove(gs, validMoves)
            if AIMove == None:
                AIMove = ai.getRandomMove(validMoves)
            gs.make_new_move(AIMove)
            animateMove(AIMove, validMoves)
            # For debugging.
            print(AIMove.get_chess_notation(), end=' ')
            moveMade = True
        
        if moveMade:
            validMoves = gs.get_valid_moves()
            if len(playerClicks) > 0:
                deselectSquare(squares[playerClicks[0]])
            squareClicked = ()
            playerClicks = []
            moveMade = False
        
        gs.findCheckmateOrStalemate(validMoves)
        drawGameState(validMoves)
        
        if gs.gameover:
            s = p.Surface((WIDTH, HEIGHT))
            s.fill((0, 0, 0))
            s.set_alpha(100)
            screen.blit(s, (0, 0))
            if gs.checkmate:
                if gs.white_to_move:
                    drawText('Black wins!', 48)
                else:
                    drawText('White wins!', 48)
            elif gs.stalemate:
                if gs.stalemate_counter > 100:
                    drawText('Stalemate', 48)
                    drawText('50 moves have gone by without\n', 36)
                    drawText('a capture or pawn move.', 36)
                else:
                    drawText('Stalemate: no legal moves.')
        
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
            IMAGES[pieceName].convert()


def drawGameState(validMoves):
    '''
    Responsible for all the graphics within a current gamestate.
    '''
    # Draw squares on the board.
    drawBoard(validMoves)
    highlightLastMove()
    # Highlight selected square and movement/capture squares.
    if selectedSquare != None:
        highlightSquares(validMoves)
    # Add in piece highlighting or move suggestions (later)
    drawPieces()  # Draw pieces on the board.


def drawBoard(validMoves):
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


def highlightSquares(validMoves):
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


def highlightLastMove():
    # Get last move.
    if len(gs.move_log) > 0:
        lastMove = gs.move_log.copy().pop()[0]
        startSquare = lastMove.start_square.get_coords()
        if lastMove.contains_castle():
            endSquare = lastMove.castle[1].get_coords()
        else:
            endSquare = lastMove.end_square.get_coords()
        if gs.upside_down:
            startSquare = FLIPPEDBOARD[startSquare[0]], FLIPPEDBOARD[startSquare[1]]
            endSquare = FLIPPEDBOARD[endSquare[0]], FLIPPEDBOARD[endSquare[1]]
        # Draw square highlights for start and end squares.
        surface = p.Surface((SQ_SIZE, SQ_SIZE))
        surface.set_alpha(80)
        surface.fill(p.Color('green'))
        screen.blit(surface, 
            (startSquare[0] * SQ_SIZE, startSquare[1] * SQ_SIZE,))
        screen.blit(surface, 
            (endSquare[0] * SQ_SIZE, endSquare[1] * SQ_SIZE,))
        

def drawPieces():
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


def animateMove(move, validMoves, undo=False):
    '''
    Animates pieces when they are moved, 
    including undoing and redoing moves.
    '''
    # Get move info.
    pieceMoved = move.piece_moved
    pieceCaptured = move.piece_captured
    startSquare, endSquare = move.start_square, move.end_square
    if undo:
        startSquare, endSquare = endSquare, startSquare
        pieceCaptured = None
    startFile, startRank = startSquare.get_coords()
    endFile, endRank = endSquare.get_coords()
    if gs.upside_down:
        startFile, startRank = FLIPPEDBOARD[startFile], FLIPPEDBOARD[startRank]
        endFile, endRank = FLIPPEDBOARD[endFile], FLIPPEDBOARD[endRank]
    endSquareColor = endSquare.get_color()
    dFile = endFile - startFile  # Change in file for the piece moved.
    dRank = endRank - startRank  # Change in rank for the piece moved.
    if move.contains_castle():
        rook, rookStartSquare, rookEndSquare = move.castle
        if undo:
            rookStartSquare, rookEndSquare = rookEndSquare, rookStartSquare
        rookStartFile, rookStartRank = rookStartSquare.get_coords()
        rookEndFile, rookEndRank = rookEndSquare.get_coords()
        if gs.upside_down:
            (rookStartFile, rookStartRank) = (
                FLIPPEDBOARD[rookStartFile], FLIPPEDBOARD[rookStartRank]
            )
        (rookEndFile, rookEndRank) = (
            FLIPPEDBOARD[rookEndFile], FLIPPEDBOARD[rookEndRank]
        )
        dRookFile = rookEndFile - rookStartFile
        dRookRank = rookEndRank - rookStartRank
        rookEndSquareColor = rookEndSquare.get_color()
    framesPerMove = MAX_FPS // 10 + 1  # Number of frames to one move.
    # moveDistance = abs(dRank) + abs(dFile)
    for frame in range(1, framesPerMove):
        drawBoard(validMoves)
        drawPieces()
        # Erase the piece being moved from its ending square.
        if endSquareColor == 'light':
            color = THEMES[theme][0]
        elif endSquareColor == 'dark':
            color = THEMES[theme][1]
        p.draw.rect(screen, color,
            p.Rect(endFile*SQ_SIZE, endRank*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        if move.contains_enpassant() and not undo:
            # Draw captured pawn on en passant square.
            epFile, epRank = move.enpassant_square.get_coords()
            screen.blit(IMAGES[pieceCaptured.get_image_name()],
                p.Rect(epFile*SQ_SIZE, epRank*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        else:
            # Draw captured piece onto end Square.
            if pieceCaptured != None:
                screen.blit(IMAGES[pieceCaptured.get_image_name()], 
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
                framesPerMove)
        drawAnimationFrame(pieceMoved, pieceCaptured, startFile, startRank, 
            dFile, dRank, endFile, endRank, frame, framesPerMove)
        
        p.display.flip()
        clock.tick(MAX_FPS)


def drawAnimationFrame(pieceMoved, pieceCaptured, startFile, startRank, dFile,
        dRank, endFile, endRank, frame, framesPerMove):
    '''
    Draws a single frame of animation.
    '''
    file, rank = (startFile + dFile*frame/framesPerMove, 
                  startRank + dRank*frame/framesPerMove)
    # Draw moving piece.
    screen.blit(IMAGES[pieceMoved.get_image_name()], 
        p.Rect(file*SQ_SIZE, rank*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def selectSquare(square):
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


def promoteMenu(move):
    '''Simple text menu for when pawns get promoted.'''
    choices = 'qkrb'
    print('What would you like to promote your Pawn to?')
    i = input('q = Queen, k = Knight, b = Bishop, r = Rook\n')
    if i[0].lower() in choices:
        gs.promote(i[0], move)
    else:
        print('Incorrect choice.')
        promoteMenu(gs, move)


def drawText(text, font_size, font='Helvetica', othickness=3, xoffset=0,
        yoffset=0):
    '''
    Draws white text with a black (pseudo-) outline centered on the screen.
    '''
    font = p.font.SysFont(font, font_size, True, False)
    textObject = font.render(text, True, (245, 245, 245))
    textRect = textObject.get_rect()
    textRect.centerx, textRect.centery = (
        screen.get_rect().centerx, screen.get_rect().centery - HEIGHT // 15
    )
# =============================================================================
#     textOutline = font.render(text, True, (28, 28, 28))
#     for i in range(1, othickness):
#         for x, y in (DIRECTIONS['HORIZONTAL'] + DIRECTIONS['VERTICAL']
#             + DIRECTIONS['DIAGONAL']):
#             screen.blit(textOutline, textRect.move(i*x, i*y))
# =============================================================================
    screen.blit(textObject, textRect)


def exitGame():
    '''Exits Pygame.'''
    p.quit()
    sys.exit()


if __name__ == '__main__':
    main()





