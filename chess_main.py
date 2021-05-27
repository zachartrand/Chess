#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Fri Mar 12 23:47:52 2021

@author: Zach Chartrand

This is the main chess program where GUI
and user interactions are programmed.
"""

import os
import sys

import pygame as p

import chess_engine
import chess_ai as ai
from chess_themes import themes
from chess_menu import mainMenu

CAPTION = 'Chess'
WIDTH = HEIGHT = 720                    # Width and height of board in pixels.
DIMENSION = 8                           # Chess board is 8 x 8 squares.
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 120                           # For animations later on.
IMAGES = {}                             # Setup for loadImages().
FLIPPEDBOARD = [i for i in reversed(range(DIMENSION))]  # For getting screen
    # coordinates when the board is drawn from Black's perspective.
UPSIDEDOWN = False


def main():
    """
    The main driver for our code.

    This will handle user input and updating the graphics.
    """
    global screen, clock, theme, gs, highlight_last_move, UPSIDEDOWN
    humanWhite, humanBlack, theme_name = mainMenu()
    if theme_name not in themes.keys():
        theme_name = "blue"
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption(CAPTION)
    clock = p.time.Clock()
    screen.fill(p.Color(28, 28, 28))
    theme = themes[theme_name]
    gs = chess_engine.GameState()
    board = gs.board
    squares = board.squares
    gs.valid_moves = gs.get_valid_moves()
    validMoves = gs.valid_moves
    moveMade = False  # Flag variable for when a move is made. Prevents engine
        # from wasting resources every frame to find all valid moves.
    loadImages()  # Only do this once, before the while loop.
    squareClicked = ()  # No initial square selected, holds last square
        # clicked by user
    playerClicks = []  # Keep track of player clicks
        # (two tuples: [(4, 6), (4, 4)] would be (e2 pawn to) e4)
    highlight_last_move = True
    # humanWhite = True  # True if human player is white.
    # humanBlack = True  # True if human player is black.
    if humanBlack and not humanWhite:
        UPSIDEDOWN = True
    
    # TODO: Add statement that saves user settings (e.g., theme) using the 
        # shelve module.
    
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
                    if UPSIDEDOWN:
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
                                    printMove(validMove)  # For debugging.
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
                    if gs.move_log:
                        board.update_pieces(gs.undo_move())
                        move = gs.undo_log.copy().pop()[0]
                        animateMove(move, validMoves, undo=True)
                        # For debugging.
                        print('Undid {}'.format(str(move)), end=' ')
                        moveMade = True
                # Redo move when CTRL+R is pressed.
                if (
                        (event.mod & p.KMOD_CTRL and event.key == p.K_y)
                         or event.key == p.K_RIGHT
                         or event.key == p.K_d
                ):
                    if gs.undo_log:
                        gs.redo_move()
                        move = gs.move_log.copy().pop()[0]
                        animateMove(move, validMoves)
                        print('Redid {}'.format(str(move)), end=' ')  # For debugging.
                        moveMade = True

        # AI move finder
        if (not moveMade and not gs.gameover and not humanTurn
                and not gs.undo_log):
            AIMove = ai.getBestMove(gs)
            if AIMove is None:
                AIMove = ai.getRandomMove(validMoves)
            p.time.wait(200)
            gs.make_new_move(AIMove)
            animateMove(AIMove, validMoves)
            printMove(AIMove)  # For debugging.
            moveMade = True
        
        if moveMade:
            gs.valid_moves = gs.get_valid_moves()
            validMoves = gs.valid_moves
            if playerClicks:
                deselectSquare(squares[playerClicks[0]])
            squareClicked = ()
            playerClicks = []
            moveMade = False

        gs.find_mate(validMoves)
        drawGameState(validMoves)

        if gs.gameover:
            s = p.Surface((WIDTH, HEIGHT))
            s.fill((0, 0, 0))
            s.set_alpha(150)
            screen.blit(s, (0, 0))
            if gs.checkmate:
                if gs.white_to_move:
                    drawText('Black wins!', 48)
                else:
                    drawText('White wins!', 48)
            elif gs.stalemate:
                if gs.stalemate_counter > 100:
                    drawText('Stalemate', 48)
                    drawText('50 moves have gone by without\n', 36, yoffset=10)
                    drawText('a capture or pawn move.', 36, yoffset=20)
                else:
                    drawText('Stalemate: no legal moves.', 36)

        clock.tick(MAX_FPS)
        p.display.flip()


def loadImages():
    """
    Initialize a global dictionary of images.

    This will be called exactly once in the main(),
    before the while: loop.
    """
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
    """
    Responsible for all the graphics within a current gamestate.
    """
    # Draw squares on the board.
    drawBoard(validMoves)
    if highlight_last_move:
        highlightLastMove()
    # Highlight selected square and movement/capture squares.
    if selectedSquare is not None:
        highlightSquares(validMoves)
    # Add in piece highlighting or move suggestions (later)
    drawPieces()  # Draw pieces on the board.


def drawBoard(validMoves):
    """
    Draw the squares on the board.
    """
    global selectedSquare
    selectedSquare = None
    squares = gs.board.squares.T.flat
    for square in squares:
        file, rank = getSquareCoordinates(square)
        if square.is_selected():
            selectedSquare = square
        color = getSquareThemeColor(square)

        p.draw.rect(
            screen, color, p.Rect(
                file * SQ_SIZE, rank * SQ_SIZE,
                SQ_SIZE, SQ_SIZE,
            )
        )


def highlightLastMove():
    """Highlights the start and end square of the last piece that moved."""
    # Get last move.
    if gs.move_log:
        lastMove = gs.move_log.copy().pop()[0]
        startSquare = lastMove.start_square
        if lastMove.contains_castle():
            endSquare = lastMove.castle[1]
        else:
            endSquare = lastMove.end_square
        startFile, startRank = getSquareCoordinates(startSquare)
        endFile, endRank = getSquareCoordinates(endSquare)
        # Draw square highlights for start and end squares.
        startSquareColor = (
            p.Color(theme[4]) if startSquare.get_color() == 'light'
            else p.Color(theme[5])
        )
        endSquareColor = (
            p.Color(theme[4]) if endSquare.get_color() == 'light'
            else p.Color(theme[5])
        )
        startSurface = p.Surface((SQ_SIZE, SQ_SIZE))
        startSurface.fill(startSquareColor)
        endSurface = p.Surface((SQ_SIZE, SQ_SIZE))
        endSurface.fill(endSquareColor)
        screen.blit(startSurface, (startFile * SQ_SIZE, startRank * SQ_SIZE))
        screen.blit(endSurface, (endFile * SQ_SIZE, endRank * SQ_SIZE))

# =============================================================================
#         surface = p.Surface((SQ_SIZE, SQ_SIZE))
#         # (76, 183, 230)
#         # (20, 144, 255)
#         surface.fill(p.Color(12, 163, 230))
#         surface.set_alpha(180)
#         screen.blit(surface, (startFile * SQ_SIZE, startRank * SQ_SIZE))
#         screen.blit(surface, (endFile * SQ_SIZE, endRank * SQ_SIZE))
# =============================================================================


def highlightSquares(validMoves):
    """
    Highlights squares on the board
    related to the current selected piece.
    """
    file, rank = getSquareCoordinates(selectedSquare)
    color = getSquareThemeHighlightColor(selectedSquare)

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
    if moveSquares:
        for square in moveSquares:
            file, rank = getSquareCoordinates(square)
            surface = p.Surface((SQ_SIZE, SQ_SIZE))
            surface.set_alpha(80)
            surface.fill(p.Color('green'))
            screen.blit(surface, (file * SQ_SIZE, rank * SQ_SIZE,))

    # Draw markers for capture squares.
    if captureSquares:
        for square in captureSquares:
            file, rank = getSquareCoordinates(square)
            attackSquare = p.Surface((SQ_SIZE, SQ_SIZE))
            attackSquare.fill((230, 118, 118))
            attackSquare.set_alpha(255)
            screen.blit(attackSquare, (file * SQ_SIZE, rank * SQ_SIZE,))
# =============================================================================
# This is for using circles instead of highlighting the square.
#             p.draw.circle(
#                 attackSquare,
#                 'red',
#                 (0.5*SQ_SIZE, 0.5*SQ_SIZE),
#                 SQ_SIZE // 2.1,
#                 6,
#             )
# =============================================================================


def drawPieces():
    """
    Draw the pieces on the board using the current GameState.board.
    """
    pieces = gs.board.get_pieces()
    for piece in pieces:
        if piece.is_on_board():  # Needed to fix AI bug, apparently.
            file, rank = getSquareCoordinates(piece.get_square())
            pieceName = piece.get_image_name()
            screen.blit(
                IMAGES[pieceName], p.Rect(
                    file * SQ_SIZE, rank * SQ_SIZE,
                    SQ_SIZE, SQ_SIZE,
                )
            )


def markMovementSquares(square, validMoves):
    """
    Finds the squares that the selected piece can move to and stores
    them as two lists.

    These lists are used in the drawBoard function to highlight move
    and capture squares of the selected piece.
    """
    moveSquares = []
    captureSquares = []
    for move in validMoves:
        if square == move.start_square:
            if (move.piece_captured is not None
                or move.contains_enpassant()):
                captureSquares.append(move.end_square)
            else:
                moveSquares.append(move.end_square)

    return moveSquares, captureSquares


def animateMove(move, validMoves, undo=False):
    """
    Animates pieces when they are moved,
    including undoing and redoing moves.
    """
    # Get move info.
    pieceMoved = move.piece_moved
    pieceCaptured = move.piece_captured
    startSquare, endSquare = move.start_square, move.end_square
    if undo:
        startSquare, endSquare = endSquare, startSquare
        pieceCaptured = None
    startFile, startRank = getSquareCoordinates(startSquare)
    endFile, endRank = getSquareCoordinates(endSquare)
    dFile = endFile - startFile  # Change in file for the piece moved.
    dRank = endRank - startRank  # Change in rank for the piece moved.
    if move.contains_castle():
        rook, rookStartSquare, rookEndSquare = move.castle
        if undo:
            rookStartSquare, rookEndSquare = rookEndSquare, rookStartSquare
        rookStartFile, rookStartRank = getSquareCoordinates(rookStartSquare)
        rookEndFile, rookEndRank = getSquareCoordinates(rookEndSquare)
        dRookFile = rookEndFile - rookStartFile
        dRookRank = rookEndRank - rookStartRank
    framesPerMove = MAX_FPS // 10 + 1  # Number of frames to one move.
    # moveDistance = abs(dRank) + abs(dFile)
    for frame in range(1, framesPerMove):
        drawBoard(validMoves)
        drawPieces()
        # Erase the piece being moved from its ending square.
        color = getSquareThemeColor(endSquare)
        p.draw.rect(screen, color,
            p.Rect(endFile*SQ_SIZE, endRank*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        if move.contains_enpassant() and not undo:
            # Draw captured pawn on en passant square.
            epFile, epRank = getSquareCoordinates(move.enpassant_square)
            screen.blit(IMAGES[pieceCaptured.get_image_name()],
                p.Rect(epFile*SQ_SIZE, epRank*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        else:
            # Draw captured piece onto end Square.
            if pieceCaptured is not None:
                screen.blit(IMAGES[pieceCaptured.get_image_name()],
                    p.Rect(endFile*SQ_SIZE, endRank*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        if move.contains_castle():
            color = getSquareThemeColor(rookEndSquare)
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
    """
    Draws a single frame of animation.
    """
    file, rank = (startFile + dFile*frame/framesPerMove,
                  startRank + dRank*frame/framesPerMove)
    # Draw moving piece.
    screen.blit(IMAGES[pieceMoved.get_image_name()],
        p.Rect(file*SQ_SIZE, rank*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def selectSquare(square):
    """
    Adds a flag to highlight the square that is clicked on if the piece
    color is the same as the turn.
    """
    if not square.is_selected():
        color = square.get_piece().get_color()
        if ((color == 'white' and gs.white_to_move)
            or (color == 'black' and not gs.white_to_move)):
            square.selected = True


def deselectSquare(square):
    """Deselects a selected square."""
    if square.is_selected():
        square.selected = False


def getSquareThemeColor(square):
    """
    Returns the square color for the given square on the chessboard
    to be rendered on screen.
    """
    if square.get_color() == 'light':
        return theme[0]
    elif square.get_color() == 'dark':
        return theme[1]


def getSquareThemeHighlightColor(square):
    """
    Returns the highlighted square color for the given square on the
    chessboard to be rendered on screen.
    """
    if square.get_color() == 'light':
        return theme[2]
    elif square.get_color() == 'dark':
        return theme[3]


def getSquareCoordinates(square):
    """
    Returns the coordinates of the given square as seen on screen.
    Takes into account whether the board is seen from Black's
    perspective.
    """
    file, rank = square.get_coords()
    if UPSIDEDOWN:
        file, rank = FLIPPEDBOARD[file], FLIPPEDBOARD[rank]

    return (file, rank)


def promoteMenu(move):
    """Simple text menu for when pawns get promoted."""
    choices = 'qkrb'
    print('What would you like to promote your Pawn to?')
    i = input('q = Queen, k = Knight, b = Bishop, r = Rook\n')
    if i[0].lower() in choices:
        gs.promote(i[0], move)
    else:
        print('Incorrect choice.')
        promoteMenu(gs, move)


def printMove(move):
    number = ''
    if move.piece_moved.get_color() == 'white':
        number = str(move.move_number//2 + 1) + '. '
    print(''.join([number, move.name]), end=' ')


def drawText(text, font_size, font='Helvetica', othickness=3, xoffset=0,
        yoffset=0):
    """
    Draws white text with a black (pseudo-) outline
    centered on the screen.
    """
    font = p.font.SysFont(font, font_size, True, False)
    textObject = font.render(text, True, (245, 245, 245))
    textRect = textObject.get_rect()
    textRect.centerx, textRect.centery = (
        screen.get_rect().centerx, screen.get_rect().centery - HEIGHT // 15
    )
# =============================================================================
# Poor man's function for making a black outline around the text. Find out if
# Pygame has a way of doing this properly.
#     textOutline = font.render(text, True, (28, 28, 28))
#     for i in range(1, othickness):
#         for x, y in (DIRECTIONS['HORIZONTAL'] + DIRECTIONS['VERTICAL']
#             + DIRECTIONS['DIAGONAL']):
#             screen.blit(textOutline, textRect.move(i*x, i*y))
# =============================================================================
    screen.blit(textObject, textRect)


def exitGame():
    """Exits Pygame."""
    p.quit()
    sys.exit()


if __name__ == '__main__':
    main()
