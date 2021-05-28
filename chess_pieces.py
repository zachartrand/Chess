# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 11:20:56 2021

@author: Zach Chartrand

This file contains classes for the chess pieces.  Should be imported by
the chess_engine module.
"""

from __future__ import annotations

__all__ = ['King', 'Queen', 'Rook', 'Bishop', 'Knight', 'Pawn']

from typing import Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from chess_board import Square
    from chess_engine import Move

DIRECTIONS = dict(
    DIAGONAL = (
        (1, -1),   # Up Left
        (-1, -1),  # Up Right
        (-1, 1),   # Down Left
        (1, 1),    # Down Right
    ),
    HORIZONTAL = (
        (-1, 0),  # Left
        (1, 0),   # Right
    ),
    VERTICAL = (
        (0, -1),  # Up
        (0, 1),   # Down
    ),
    KNIGHT = (
        (-1, -2),  # Up 2, Left 1
        (1, -2),   # Up 2, Right 1
        (-1, 2),   # Down 2, Left 1 
        (1, 2),    # Down 2, Right 1
        (-2, -1),  # Left 2, Up 1
        (-2, 1),   # Left 2, Down 1
        (2, -1),   # Right 2, Up 1
        (2, 1),    # Right 2, Down 1
    ),
)


class Piece:
    """
    Super class for the different chess pieces.
    
    The only input needed to create a piece is the color of the
    piece. The type of piece is determined by the subclass called
    when creating the Piece object. This class should never be
    used to create an object outside of its subclasses.
    """    
    def __init__(self, color: str) -> None:
        """
        Args:
            color - 'white' or 'black'
        """
        # Piece.name and Piece.symbol are set in subclasses. Methods
        # using Piece.name and Piece.symbol should not raise errors as
        # long as objects are created only through Piece's subclasses.
        if color.lower().startswith('w'):
            self.color = 'white'
        elif color.lower().startswith('b'):
            self.color = 'black'
        else:
            raise ValueError("The Piece's color must be 'white' or 'black'.")
        self.square = None   # Square will be set later, start with None.
        self.first_move = None  # Store piece's first move. Used for castling
            # and en passant.
        self.pin_direction = ()  # Direction from which a piece is pinned.
        self.image_name = self.color[0] + self.symbol  # Image filename for the
            # piece.
        
    def __eq__(self, other) -> bool:
        """Return self == other."""
        pieceType = type(self)
        if isinstance(other, pieceType):
            if id(self) == id(other):
                return True
        
        return False
    
    def __hash__(self) -> int:
        """Return hash(self)."""
        return hash((self.name, self.color, id(self)))
    
    def __repr__(self) -> str:
        """Return repr(self)."""
        return (f'self.__class__.__name__('
                f"'{self.color}')")
    
    def __str__(self) -> str:
        """Return str(self)."""
        return self.get_fullname()
    
    def get_color(self) -> str:
        """
        Returns a string of the piece's color,
        either 'white' or 'black'.
        """
        return self.color
    
    def get_square(self) -> Square:
        """Returns the square object that the piece occupies."""
        return self.square
    
    def get_coords(self) -> Tuple[int]:
        """
        Returns the coordinates of the piece if the piece is on the
        board.
        
        The value returned is a tuple of the form
        
            file, rank
        
        where both file and rank are indices from 0 to the board
        width/height - 1.
        """
        if self.is_on_board():
            return self.square.get_coords()
        
        return ()
    
    def get_square_name(self) -> str:
        """
        Returns the name of the square that the piece is on.
        
        If the piece is on a square, this will return the square's name
        in algebraic notation.  Otherwise, it will state that the piece
        is not on a square.
        """
        if self.square is not None:
            return self.square.get_name()
        
        return ''
    
    def get_square_color(self) -> str:
        """
        Returns the color of the square that the piece is on.
        
        Useful for Bishops (light-square vs. dark-square bishop).
        """
        return self.square.get_color()
    
    def set_square(self, square: Square) -> None:
        """
        Assigns a Square object to the Piece and then assigns the Piece
        to that same Square object.
        """
        self.square = square
        square.piece = self
    
    def is_on_board(self) -> bool:
        """
        Returns whether the piece is on the board or not.
        
        Returns True if the piece is on a square, otherwise returns
        False.
        """
        if self.square is not None:
            return True
        
        return False
        
    def get_name(self) -> str:
        """
        Returns the name of the piece.
        
        Returns a string of the piece's name, e.g. for a Queen, this
        function returns 'Queen'.
        """
        return self.name
    
    def get_symbol(self) -> str:
        """
        Returns the one-letter symbol for the piece in algebraic
        notation, e.g., the Knight is denoted by an 'N'.
        """
        return self.symbol
    
    def get_fullname(self) -> str:
        """
        Returns a human-readable string of the piece, its color, and
        the square it's on if assigned to a square.
        """
        fullname = []
        if not self.is_on_board():
            fullname.append('Off-the-board')
        fullname.append(self.get_color().title())
        fullname.append(self.get_name().title())
        if self.is_on_board():
            fullname.append('on')
            fullname.append(self.get_square_name())
        
        return ' '.join(fullname)
    
    def get_image_name(self) -> str:
        """
        Returns piece's image filename as a string.
        
        Used for importing images and rendering pieces in the game.
        """
        return self.image_name
    
    def remove(self) -> None:
        """
        Removes the piece from a square on the board if the
        piece is on the board.
        """
        if self.is_on_board():
            self.square.remove_piece(self)
    
    def has_moved(self) -> bool:
        """
        Returns True if the piece hasn't moved on the board.
        Used for castling and two-square pawn moves.
        """
        if self.first_move is not None:
            return True
        
        return False
    
    def get_first_move(self) -> Move:
        """Returns the first move of the piece if it has one."""
        if self.has_moved():
            return self.first_move
        
        return None
    
    def is_pinned(self) -> bool:
        """Returns True if the piece is pinned to the King."""
        if len(self.pin_direction) > 0:
            return True
        
        return False
    
    def get_pin_direction(self) -> Tuple[int]:
        """Returns the direction a pin is coming from."""
        return self.pin_direction
    
    def get_directions(self) -> Tuple[Tuple[int]]:
        """
        Returns the directions that the piece can move in.
        
        Each direction is a tuple with a 0 or 1 in the x and y
        direction. For example, right and down is represented as
        (1, 1). This method returns a tuple of direction tuples. Used
        for determining squares that the piece can move in.
        """
        return self.directions


class Rook(Piece):
    """
    Class for the Rook piece.
    
    The Rook is the castle piece. Moves in rows with no limit to how
    far it can move on the board.
    """
    def __init__(self, color: str) -> None:
        self.name = 'Rook'
        self.symbol = 'R'
        
        super().__init__(color)
        
        self.directions = DIRECTIONS['HORIZONTAL'] + DIRECTIONS['VERTICAL']
    

class King(Piece):
    """
    Class for the King piece.
    
    Most valuable piece in the game.  If the King is captured, the game
    is over.  Moves one (1) square in any direction.
    """
    def __init__(self, color: str) -> None:
        self.name = 'King'
        self.symbol = 'K'
        
        super().__init__(color)
        
        self.directions = (
            DIRECTIONS['HORIZONTAL'] 
            + DIRECTIONS['VERTICAL'] 
            + DIRECTIONS['DIAGONAL']
        )
    

class Queen(Piece):
    """
    Class for the Queen piece.
    
    The Queen is arguably the best piece in the game.  It can move both
    as a rook and a bishop, i.e. any number of squares vertically,
    horizontally, or diagonally.
    """
    def __init__(self, color: str) -> None:
        self.name = 'Queen'
        self.symbol = 'Q'
        
        super().__init__(color)
        
        self.directions = (
            DIRECTIONS['HORIZONTAL'] 
            + DIRECTIONS['VERTICAL'] 
            + DIRECTIONS['DIAGONAL']
        )
    

class Knight(Piece):
    """
    Class for the Knight piece.
    
    A minor piece that moves in an L-pattern. Can jump over pieces.
    Always moves to an opposite-color square.
    
    Also known as a Horse by plebs.
    """
    def __init__(self, color: str) -> None:
        self.name = 'Knight'
        self.symbol = 'N'
        
        super().__init__(color)
        
        self.directions = DIRECTIONS['KNIGHT']
    

class Bishop(Piece):
    """
    Class for the Bishop piece.
    
    A minor piece that moves diagonally any number of squares. Can only
    move on squares of the same color.
    """
    def __init__(self, color: str) -> None:
        self.name = 'Bishop'
        self.symbol = 'B'
        
        super().__init__(color)
        
        self.directions = DIRECTIONS['DIAGONAL']


class Pawn(Piece):
    """
    Class for the Pawn piece.
    
    The front line of your army.  Can move one (1) square forward, two
    (2) squares forward as its first move, and attacks diagonally
    forward.
    """
    def __init__(self, color: str) -> None:
        self.name = 'Pawn'
        self.symbol = 'P'
        
        super().__init__(color)
        
        if self.color == 'white':
            self.directions = DIRECTIONS['VERTICAL'][0]
            self.promotion_rank = 0
        elif self.color == 'black':
            self.directions = DIRECTIONS['VERTICAL'][1]
            self.promotion_rank = 7
        
    def get_promotion_rank(self) -> int:
        """Returns the rank that the Pawn will promote at."""
        return self.promotion_rank
    
    def can_promote(self) -> bool:
        """Returns whether a pawn can promote."""
        rank = self.get_coords()[1]
        if rank + self.directions[1] == self.get_promotion_rank():
            return True
        
        return False




