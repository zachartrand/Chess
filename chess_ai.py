# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 11:26:24 2021

@author: Zach
"""

import random as rn
# from numba import njit


__all__ = [
    'getRandomMove', 'getBestMove'
]

PIECE_SCORE = dict(
    King = 9000,
    Queen = 9,
    Rook = 5,
    Bishop = 3,
    Knight = 3,
    Pawn = 1,
)
CHECKMATE = PIECE_SCORE['King'] + 1
STALEMATE = 0
MAX_DEPTH = 2


def getRandomMove(validMoves):
    '''Picks and returns a random move.'''
    return validMoves[rn.randint(0, len(validMoves)-1)]


def getBestMinMaxMove(gs, validMoves):
    '''
    Find the best move based on material alone.
    '''
    turnMultiplier = 1 if gs.white_to_move else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    rn.shuffle(validMoves)
    for playerMove in validMoves:
        gs.make_move(playerMove)
        opponentsMoves = gs.get_valid_moves()
        if gs.stalemate:
            opponentMaxScore = STALEMATE
        elif gs.checkmate:
            opponentMaxScore = -CHECKMATE
        else:
            opponentMaxScore = -CHECKMATE
            for opponentsMove in opponentsMoves:
                gs.make_move(opponentsMove)
                gs.get_valid_moves()
                if gs.checkmate:
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board)
                if score > opponentMaxScore:
                    opponentMaxScore = score
                gs.undo_move()
                gs.undo_log.pop()
        
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undo_move()
        gs.undo_log.pop()
    
    return bestPlayerMove


def getBestMove(gs, validMoves):
    '''Helper function to make the first recursive call.'''
    global nextMove
    nextMove = None
    getNegaMaxMove(gs, validMoves, MAX_DEPTH, 1 if gs.white_to_move else -1)
    return nextMove


def getMinMaxMove(gs, validMoves, whiteToMove, depth):
    '''Recursive function for finding the best AI move.'''
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)
    
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.make_move(move)
            nextMoves = gs.get_valid_moves()
            score = getMinMaxMove(gs, nextMoves, False, depth-1)
            if score > maxScore:
                maxScore = score
                if depth == MAX_DEPTH:
                    nextMove = move
            gs.undo_move()
            gs.undo_log.pop()
        
        return maxScore
    
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.make_move(move)
            nextMoves = gs.get_valid_moves()
            score = getMinMaxMove(gs, nextMoves, True, depth-1)
            if score < minScore:
                minScore = score
                if depth == MAX_DEPTH:
                    nextMove = move
            gs.undo_move()
            gs.undo_log.pop()
        
        return minScore


def getNegaMaxMove(gs, validMoves, depth, turnMultiplier):
    '''
    
    '''
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.make_move(move)
        nextMoves = gs.get_valid_moves()
        score = -1 * getNegaMaxMove(gs, nextMoves, depth-1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == MAX_DEPTH:
                nextMove = move
        if abs(score) == CHECKMATE:
            break
        
        gs.undo_move()
        gs.undo_log.pop()
    
    return maxScore


def scoreBoard(gs):
    '''
    Scores the board based on material and attacks.
    
    A positive score is good for white, and a negative score is good for black.
    '''
    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE
    
    board = gs.board
    score = 0
    for piece in board.get_pieces():
        if piece.get_color() == 'white':
            score += PIECE_SCORE[piece.get_name()]
        elif piece.get_color() == 'black':
            score -= PIECE_SCORE[piece.get_name()]
    
    return score


def scoreMaterial(board):
    '''
    Score the board based on material.
    '''
    score = 0
    for piece in board.get_pieces():
        if piece.get_color() == 'white':
            score += PIECE_SCORE[piece.get_name()]
        elif piece.get_color() == 'black':
            score -= PIECE_SCORE[piece.get_name()]
    
    return score









