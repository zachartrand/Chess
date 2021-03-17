# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 15:26:48 2021

@author: Zach
"""

import numpy as np  # We'll use a numpy array for the board.

FILE = 'abcdefgh'  # Letters are used to denote files.
RANK = '87654321'  # Numbers are used to denote ranks.


def defineFILEandRANK(files, ranks):
    '''
    Creates FILE and RANK globals for converting between computer and algebraic
    notations.  Only run for board sizes other than 8 x 8.  Placed in here for 
    potential compatability for odd chess variants and puzzles.
    '''
    alpha = 'abcdefghijklmnopqrstuvwxyz'
    fileList = []
    rankList = []
    for file in range(files):
        fileList.append(alpha[file])
    for rank in reversed(range(0, ranks)):
        rankList.append(str(rank))
    
    return fileList, rankList
    

def algebraicToComputer(coordinate):
    '''
    Takes algebraic notation for a square and converts it to a tuple that is 
    readable by the computer.  For example, 
    
        algebraicToComputer("a8") == (0, 0)
        
    For the inverse function, see computerToAlgebraic().
    '''
    file = FILE.index(coordinate[0])
    rank = RANK.index(coordinate[1])
    
    return file, rank
    

def computerToAlgebraic(file, rank):
    '''
    Takes the computer's coordinates for a square and converts it into a string
    in algebraic notation.  For example, 
    
        computerToAlgebraic((0, 1)) == 'a2'
        
    For the inverse function, see algebraicToComputer().
    '''
    file = FILE[file]
    rank = RANK[rank]
    
    return file + rank
    

def getSquareColor(file, rank):
    '''
    Returns the color of the square on the chess board.
    '''
    if (rank % 2 == file % 2):
        return 'light'
    else:
        return 'dark'
    

class Square:
    '''
    A square on the chess board.
    
    The attributes that identify a square are its coordinates, i.e. its file 
    and rank, so these are required when initiallizing a Square object.  
    Upon creation, the Square's file (column), rank (row), color (light or 
    dark square), and name (i.e. 'a1') are set.  The self.piece attribute is 
    set to None to denote an empty Square.  A piece can be set later with the 
    self.set_piece() method.
    '''
    
    def __init__(self, file, rank, board):
        self.file = file
        self.rank = rank
        self.color = getSquareColor(file, rank)
        self.piece = None
        self.name = computerToAlgebraic(file, rank)
        self.board = board
        self.selected = False
    
    def get_file(self):
        '''Returns the file of the square as an integer from 0 - 7.'''
        return self.file
    
    def get_rank(self):
        '''Returns the rank of the square as an integer from 0 - 7.'''
        return self.rank
    
    def get_coords(self):
        '''Returns the coordinates of the square as a tuple of (file, rank).'''
        return self.file, self.rank
    
    def get_color(self):
        '''
        Returns a string that says if the Square is 
        a light square or dark square.
        '''
        return self.color
    
    def get_name(self):
        '''Returns the name of the square in algebraic notation as a string.'''
        return self.name
    
    def get_piece(self):
        '''
        Returns the Piece object that occupies the square.  
        Otherwise, returns None.
        '''
        return self.piece
    
    def has_piece(self):
        '''Returns True if there is a piece on the square, else False.'''
        if self.piece != None:
            return True
        
        return False
    
    def get_piece_name(self):
        '''Returns a string stating which piece is on the square.'''
        if self.piece:
            return self.piece.get_name()
        else:
            return 'There is no piece on {}.'.format(self.get_name())
    
    def set_piece(self, piece):
        '''
        Sets a Piece object to the Square, and simultaneously 
        sets the Square to the Piece object.
        '''
        self.piece = piece        
        piece.square = self
        
    def remove_piece(self):
        '''Removes the piece from the square.'''
        self.piece = None
    
    def get_board(self):
        return self.board
    
    def has_friendly_piece(self, piece):
        '''
        Determines if the piece on the given square is the same color as the 
        given piece.
        '''
        if self.has_piece():
            if piece.get_color() == self.get_piece().get_color():
                return True
            
        return False
    
    def has_enemy_piece(self, piece):
        '''
        Determines if the piece on the given square is the opposite color of the 
        given piece.
        '''
        if self.has_piece():
            if piece.get_color() != self.get_piece().get_color():
                return True
            
        return False
    

class Board:
    '''
    Chess board object. 
    
    Upon creation, makes a board of numFiles x numRanks Square objects saved 
    to a numpy array.  The coordinates of the array correspond to the Square's
    coordinates.
    '''
    
    def __init__(self, numFiles=8, numRanks=8):
        if (numFiles != 8 or numRanks != 8):
            global FILE, RANK
            FILE, RANK = defineFILEandRANK(numFiles, numRanks)
        
        self.files = numFiles
        self.ranks = numRanks
        self.pieces = np.array([], dtype=object)  # For iterating through 
            # pieces on the board.  Will be populated when pieces are added.
        
        emptyBoard = []
        # for _ in range(numFiles):
        #     emptyBoard.append([])
        for file in range(numFiles):
            for rank in range(numRanks):
                emptyBoard.append(Square(file, rank, self))
        self.squares = np.array(
            emptyBoard, dtype=object
            ).reshape((self.files, self.ranks))
    
    def get_size(self):
        '''
        Gives the dimensions of the board.  
        
        Returns a tuple of the form
        
            (files, ranks).
        '''
        return self.files, self.ranks
    
    def update_pieces(self):
        '''
        Updates the Board's pieces attribute by removing captured pieces 
        and adding new ones (e.g., from Pawn promotion).
        '''
        pieces = []
        squares = self.squares.T.flat
        for square in squares:
            if square.has_piece():
                pieces.append(square.get_piece())
        
        self.pieces = np.array(pieces, dtype=object)
                
        
    def get_pieces(self):
        '''Returns an array of pieces currently on the board.'''
        return self.pieces










