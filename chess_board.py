# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 15:26:48 2021

@author: Zach

This module contains the Square and Board class as well as functions that they
use.
"""

__all__ = [
    "Board", "Square"
]

import numpy as np  # We'll use a numpy array for the board.

from chess_pieces import King, Queen, Rook, Bishop, Knight, Pawn

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
        if self.has_piece():
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
        if self.has_piece():
            self.piece.square = None
            self.piece = None
        
    def get_board(self):
        '''Returns the Board object that the square belongs to.'''
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
        Determines if the piece on the given square is the opposite color of
        the given piece.
        '''
        if self.has_piece():
            if piece.get_color() != self.get_piece().get_color():
                return True
            
        return False
    
    def is_selected(self):
        '''
        Returns True if the square is currently selected by the player.
        Otherwise, returns False.
        '''
        return self.selected
    

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
        self.pieces = []  # For iterating through pieces on the board.
            # Will be populated when pieces are added.
        self.queens, self.rooks, self.knights, self.bishops = (
            {'white': [], 'black': []}, {'white': [], 'black': []},
            {'white': [], 'black': []}, {'white': [], 'black': []},
        )  # For iterating to find if multiple pieces of the same type and 
           # color are on the same file or rank.
        self.piece_lists = dict(
            Queen = self.queens,
            Rook = self.rooks,
            Knight = self.knights,
            Bishop = self.bishops,
        )
        
        emptyBoard = []
        # for _ in range(numFiles):
        #     emptyBoard.append([])
        for file in range(numFiles):
            for rank in range(numRanks):
                emptyBoard.append(Square(file, rank, self))
        self.squares = np.array(
            emptyBoard, dtype=object
            ).reshape((self.files, self.ranks))
        # Make attributes for each of the kings. Will be set when the board is 
        # generated. Will be used for checks and pins.
        self.white_king = None
        self.black_king = None
    
    def get_size(self):
        '''
        Gives the dimensions of the board.  
        
        Returns a tuple of the form
        
            files, ranks.
        '''
        return self.files, self.ranks
    
    def update_pieces(self, /, pieces_set=[], pieces_removed=[]):
        '''
        Updates the Board's pieces attribute by removing captured pieces 
        and adding new ones (e.g., from Pawn promotion).
        '''
        if not self.pieces:
            # If the board hasn't had its pieces attribute set, iterate through
            # all of the squares and add the pieces to their relevant lists.
            for square in self.squares.flat:
                if square.has_piece():
                    piece = square.get_piece()
                    name = piece.get_name()
                    color = piece.get_color()
                    self.pieces.append(piece)
                    if name in self.piece_lists.keys():
                        self.piece_lists[name][color].append(piece)
        
        else:
            # If pieces are removed or added to the board, 
            # remove/add them to their relevant lists.
            if pieces_set:
                for piece in reversed(pieces_set):
                    name = piece.get_name()
                    color = piece.get_color()
                    self.pieces.append(piece)
                    if name in self.piece_lists.keys():
                        self.piece_lists[name][color].append(piece)
            if pieces_removed:
                for piece in reversed(pieces_removed):
                    name = piece.get_name()
                    color = piece.get_color()
                    self.pieces.remove(piece)
                    if name in self.piece_lists.keys():
                        self.piece_lists[name][color].remove(piece)
    
    def get_pieces(self):
        '''Returns a list of pieces currently on the board.'''
        return self.pieces


def makeStandardBoard():
    '''
    Sets up a chessboard with beginning setup of pieces.

    Returns a Board object populated with pieces.
    '''
    board = Board()  # Create an empty chessboard.
    # First, set the pawns.
    for file in range(8):
        board.squares[file, 6].set_piece(Pawn('white'))
        board.squares[file, 1].set_piece(Pawn('black'))
    # Set the Rooks.
    for file in (0, 7):
        board.squares[file, 7].set_piece(Rook('white'))
        board.squares[file, 0].set_piece(Rook('black'))
    # Set the Knights.
    for file in (1, 6):
        board.squares[file, 7].set_piece(Knight('white'))
        board.squares[file, 0].set_piece(Knight('black'))
    # Set the Bishops.
    for file in (2, 5):
        board.squares[file, 7].set_piece(Bishop('white'))
        board.squares[file, 0].set_piece(Bishop('black'))
    # Set the Queens.
    board.squares[3, 7].set_piece(Queen('white'))
    board.squares[3, 0].set_piece(Queen('black'))
    # Finally, set the Kings.
    board.white_king = King('white')
    board.squares[4, 7].set_piece(board.white_king)
    board.black_king = King('black')
    board.squares[4, 0].set_piece(board.black_king)

    board.update_pieces()

    return board


def makeTwoRooksEndgameBoard(rookColor):
    '''
    Sets up a chess board with two rooks and a king versus the other king.
    
    rookColor is either 'white' or 'black', depending on which king you want
    the rooks to be allied with.
    '''
    board = Board()
    if rookColor.lower().startswith('w'):
        rookColor = 'white'
        rank = 7
    elif rookColor.lower().startswith('b'):
        rookColor = 'black'
        rank = 0
    else:
        print("rookColor must be either 'black' or 'white'.")
        return None
    
    # Set the Rooks.
    for file in (0, 7):
        board.squares[file, rank].set_piece(Rook(rookColor))
    # Set the Kings.
    board.white_king = King('white')
    board.squares[4, 7].set_piece(board.white_king)
    board.black_king = King('black')
    board.squares[4, 0].set_piece(board.black_king)
    
    board.update_pieces()
    
    return board

def makeQueenEndgameBoard(queenColor):
    '''
    Sets up a chess board with two rooks and a king versus the other king.
    
    rookColor is either 'white' or 'black', depending on which king you want
    the rooks to be allied with.
    '''
    board = Board()
    if queenColor.lower().startswith('w'):
        queenColor = 'white'
        rank = 7
    elif queenColor.lower().startswith('b'):
        queenColor = 'black'
        rank = 0
    else:
        print("queenColor must be either 'black' or 'white'.")
        return None
    
    # Set the Queen.
    for file in (0, 7):
        board.squares[file, rank].set_piece(Queen(queenColor))
    # Set the Kings.
    board.white_king = King('white')
    board.squares[4, 7].set_piece(board.white_king)
    board.black_king = King('black')
    board.squares[4, 0].set_piece(board.black_king)
    
    board.update_pieces()
    
    return board


