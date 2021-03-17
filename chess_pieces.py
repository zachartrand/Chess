# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 11:20:56 2021

@author: Zach Chartrand

This file contains classes for the chess pieces.  Should be imported by the 
chess_engine module.
"""

__all__ = [
    'King', 'Queen', 'Rook', 'Bishop', 'Knight', 'Pawn'
]

class Piece:
    '''Super class for the different chess pieces.'''
    
    def __init__(self, color):
        self.square = None   # Square will be set later, start with None.
        self.name = ''       # Names will be set in subclasses.
        self.symbol = ''     # Symbols will be set in subclasses.
        self.image_name = '' # Image filename for the piece. Set in subclasses.
        self.is_attacked = False  # Used to tell if King is in check?
        self.first_move = None  # Store piece's first move.  Used for castling.
        
        if color.lower().startswith('w'):
            self.color = 'white'
        elif color.lower().startswith('b'):
            self.color = 'black'
        else:
            raise ValueError("color must be 'white' or 'black'.")
    
    def get_color(self):
        '''Returns a string of the piece's color, either 'white' or 'black'.'''
        return self.color
    
    def get_square(self):
        '''Returns the square object that the piece occupies.'''
        return self.square
    
    def get_coords(self):
        return self.square.get_coords()
    
    def get_square_name(self):
        '''
        Returns the name of the square that the piece is on.
        
        If the piece is on a square, this will return the square's name in
        algebraic notation.  Otherwise, it will state that the piece is not
        on a square.
        '''
        if self.square is not None:
            return self.get_square().get_name()
        else:
            return 'This piece is not on a square.'
    
    def get_square_color(self):
        '''
        Returns the color of the square that the piece is on.  
        
        Useful for Bishops (light-square vs. dark-square bishop).
        '''
        return self.square.get_color()
    
    def set_square(self, square):
        '''
        Assigns a Square object to the Piece and then assigns the Piece to 
        that same Square object.
        '''
        self.square = square
        square.piece = self
    
    def is_on_board(self):
        '''Returns whether the piece is on the board or not.'''
        if self.square != None:
            return True
        
        return False
        
    def get_name(self):
        '''Returns a string of the name of the piece.'''
        return self.name
    
    def get_symbol(self):
        '''
        Returns the one-letter symbol for the piece in algebraic notation, 
        e.g., the Knight is denoted by an 'N'. For pawns, this returns 
        an empty string.
        '''
        return self.symbol
    
    def get_fullname(self):
        '''
        Returns a human-readable string of the piece, its color, and the 
        square it's on if assigned to a square.
        '''
        fullname = []
        fullname.append(self.get_color().title())
        fullname.append(self.get_name().title())
        if self.get_square() is not None:
            fullname.append(self.get_square_name())
        
        return ('{} {} on {}.'.format(fullname[0], fullname[1], fullname[2]))
    
    def get_image_name(self):
        '''
        Returns piece's image filename as a string.
        
        Used for importing images and rendering pieces in the game.
        '''
        return self.image_name
    
    def remove(self):
        if self.is_on_board():
            self.square = None
    
    def has_moved(self):
        '''
        Returns True if the piece hasn't moved on the board. 
        Used for castling.
        '''
        if self.first_move != None:
            return True
        
        return False
        

class Rook(Piece):
    '''
    Class for the Rook piece.
    
    The Rook is the castle piece.  
    Moves in rows with no limit to how far it can move on the board.
    '''
    
    def __init__(self, color):
        super().__init__(color)
        self.name = 'Rook'
        self.symbol = 'R'
        self.image_name = self.color[0] + self.symbol
    

class King(Piece):
    '''
    Class for the King piece.
    
    Most valuable piece in the game.  If the King is captured, 
    the game is over.  Moves one (1) square in any direction.
    '''
    
    def __init__(self, color):
        super().__init__(color)
        self.name = 'King'
        self.symbol = 'K'
        self.image_name = self.color[0] + self.symbol
    

class Queen(Piece):
    '''
    Class for the Queen piece.
    
    The Queen is arguably the best piece in the game.  It can move both as a 
    rook and a bishop, i.e. any number of squares vertically, horizontally, or 
    diagonally.
    '''
    
    def __init__(self, color):
        super().__init__(color)
        self.name = 'Queen'
        self.symbol = 'Q'
        self.image_name = self.color[0] + self.symbol
    

class Knight(Piece):
    '''
    Class for the Knight piece.
    
    A minor piece that moves in an L-pattern.  Can jump over pieces.  
    Also known as a Horse by plebs.
    '''
    
    def __init__(self, color):
        super().__init__(color)
        self.name = 'Knight'
        self.symbol = 'N'
        self.image_name = self.color[0] + self.symbol
    

class Bishop(Piece):
    '''
    Class for the Bishop piece.
    
    A minor piece that moves diagonally any number of squares.
    '''
    
    def __init__(self, color):
        super().__init__(color)
        self.name = 'Bishop'
        self.symbol = 'B'
        self.image_name = self.color[0] + self.symbol
    

class Pawn(Piece):
    '''
    Class for the Pawn piece.
    
    The front line of your army.  Can move one (1) square forward, two (2) 
    squares forward as its first move, and attacks diagonally forward.
    '''
    
    def __init__(self, color):
        super().__init__(color)
        self.name = 'Pawn'
        self.symbol = ''  # Pawn moves are denoted by the square they moved to,
            # no symbol for pawn.
        self.image_name = self.color[0] + 'P'










