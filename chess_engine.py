# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 22:29:53 2021

@author: Zach Chartrand

This is the engine that will run the chess game.
"""

# import numpy as np

from chess_pieces import King, Queen, Rook, Bishop, Knight, Pawn
from chess_board import Board


class GameState():
    '''
    This class is responsible for storing all the information about the current
    state of a chess game. It will also be responsible for determining the 
    valid moves at the current state. It will also keep a move log.
    '''
    
    def __init__(self):
        self.board = makeStandardBoard()
        self.file_size, self.rank_size = (
            self.board.get_size()[0], self.board.get_size()[1]
        )
        self.white_to_move = True
        self.move_log = []
        self.undo_log = []
        self.move_branches = []
        self.move_number = 0
        self.move_functions = {
            'Pawn': (self.get_pawn_moves,),
            'Knight': (self.get_knight_moves,),
            'Bishop': (self.get_diagonal_moves,),
            'Rook': (self.get_file_moves, self.get_rank_moves),
            'Queen': (
                self.get_diagonal_moves, 
                self.get_file_moves, self.get_rank_moves
            ),
            'King': (
                self.get_diagonal_moves, 
                self.get_file_moves, self.get_rank_moves
            ),
        }
        
    def make_new_move(self, move):
        '''
        Makes a new move outside of the moves in the move_log and undo_log.
        
        Saves the current branch of moves to the move_branches attribute, then
        clears the undo_log.
        '''
        if len(self.undo_log) != 0:
            # Clear undo_log after new move if different from previous move.
            self.move_branches.append(self.undo_log)
            self.undo_log.clear()
        self.make_move(move)
        
        
    def make_move(self, move):
        '''
        Takes a Move as a parameter and executes the move.
        
        Does not work for castling, en passant, or pawn promotion.
        '''
        if move.piece_captured != None:
            move.end_square.remove_piece()
        move.end_square.set_piece(move.piece_moved)
        move.start_square.remove_piece()
        self.move_log.append(move)
        if not move.piece_moved.has_moved():
            move.piece_moved.first_move = move
            
        self.white_to_move = not self.white_to_move
        if self.white_to_move:
                self.move_number += 1
        self.board.update_pieces()
        
        # For debugging moves.
        print(move.get_chess_notation(), end=' ')
    
    def undo_move(self):
        '''Method to undo a chess move.'''
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            move.end_square.remove_piece()
            move.start_square.set_piece(move.piece_moved)
            if move.piece_captured != None:
                move.end_square.set_piece(move.piece_captured)
            self.white_to_move = not self.white_to_move
            if not self.white_to_move:
                self.move_number -= 1
            self.undo_log.append(move)
            self.board.update_pieces()
            
            # For debugging.
            print('Undid {}.'.format(move.get_chess_notation()), end=' ')  
        
    def redo_move(self):
        '''Redo a previously undone move.'''
        if len(self.undo_log) != 0:
            move = self.undo_log.pop()
            # For debugging.
            print('Redid ', end='')
            self.make_move(move)
            
            
        
    def get_valid_moves(self):
        '''
        Get all moves considering checks.
        
        1. Generate all possible moves.
        2. For each move, make the move.
        3. Generate all opponent's moves on their upcoming turn.
        4. For each of the opponent's moves, see if they attack the King.
        5. If the opponent does attack the King, it's not a valid move.
        '''
        return self.get_all_moves()
        
    def get_all_moves(self):
        '''Get all moves without considering checks.'''
        moves = []
        for piece in self.board.get_pieces():
            turn = piece.get_color()
            if (
                (turn == 'white' and self.white_to_move)
                or (turn == 'black' and not self.white_to_move)
            ):
                for func in self.move_functions[piece.get_name()]:
                    func(piece, moves, self.move_number)
        
        return moves
    
    def get_pawn_moves(self, pawn, moves, moveNumber):
        '''
        Gets all possible moves for the Pawn.
        
        Allows for double move on beginning rank, forward movement unless 
        obstructed by a piece, and diagonal capture.
        '''
        s = self.board.squares
        f, r = pawn.get_coords()
        if pawn.get_color() == 'black':
            if r + 1 < self.rank_size:
                if not s[f, r + 1].has_piece():
                    moves.append(Move(s[f, r], s[f, r + 1], moveNumber))
            # Double move on first turn.
            if r == 1:
                if not s[f, r + 2].has_piece():
                    moves.append(Move(s[f, r], s[f, r + 2], moveNumber))
            # Black Pawn captures.
            # Look to see if the square down 1 and to the right 1 has a piece 
            # to capture. 
            if (
                f + 1 < self.file_size
                and r + 1 < self.rank_size
            ):
                if (
                    s[f + 1, r + 1].has_piece()
                    and s[f + 1, r + 1].has_enemy_piece(pawn)
                ):
                    moves.append(Move(s[f, r], s[f + 1, r + 1], moveNumber))
            if (
                f - 1 >= 0 
                and r + 1 < self.rank_size
            ):
                if (
                    self.board.squares[f - 1, r + 1].has_piece()
                    and s[f - 1, r + 1].has_enemy_piece(pawn)
                ):
                    moves.append(Move(s[f, r], s[f - 1, r + 1], moveNumber))
        if pawn.get_color() == 'white':
            # White Pawn forward moves.
            if r - 1 >= 0:
                if not s[f, r - 1].has_piece():
                    moves.append(Move(s[f, r], s[f, r - 1], moveNumber))
            # Double move on first turn.
            if r == 6:
                if not s[f, r - 2].has_piece():
                    moves.append(Move(s[f, r], s[f, r - 2], moveNumber))
            # White Pawn captures.
            if (
                f + 1 < self.file_size
                and r - 1 >= 0
            ):
                if (
                    s[f + 1, r - 1].has_piece()
                    and s[f + 1, r - 1].has_enemy_piece(pawn)
                ):
                    moves.append(Move(s[f, r], s[f + 1, r - 1], moveNumber))
            if f - 1 >= 0 and r - 1 >= 0:
                if (
                    s[f - 1, r - 1].has_piece()
                    and s[f - 1, r - 1].has_enemy_piece(pawn)
                ):
                    moves.append(Move(s[f, r], s[f - 1, r - 1], moveNumber))
            
    def get_knight_moves(self, knight, moves, moveNumber):
        '''
        Generate moves for the Knight piece.
        
        The Knight is the only piece that can jump, so the only thing this needs 
        to do is check the, at most, eight (8) squares that it could move to and 
        see if a friendly piece is there.  The Knight moves in an L shape: 2 
        squares in one direction, and 1 move to the side.
        '''
        f, r = knight.get_coords()
        knightMoves = [
            (f + 2, r + 1),
            (f + 2, r - 1),
            (f - 2, r + 1),
            (f - 2, r - 1),
            (f + 1, r + 2),
            (f - 1, r + 2),
            (f + 1, r - 2),
            (f - 1, r - 2)
        ]
        s = self.board.squares
        for file, rank in knightMoves:
            if (
                (file < self.file_size 
                and rank < self.rank_size)
                and (file >= 0 and rank >= 0)
            ):
                if (
                        s[file, rank].has_piece() 
                        and (s[file, rank].has_enemy_piece(knight))
                ):
                    moves.append(Move(s[f, r], s[file, rank], moveNumber))
                elif not s[file, rank].has_piece():
                    moves.append(Move(s[f, r], s[file, rank], moveNumber))
                    
    def find_moves_on_path(self, piece, direction, moves, moveNumber):
        '''
        Finds all squares along a horizontal, vertical, or diagonal path and 
        adds them to the move list.
        '''
        start_square = piece.get_square()
        for square in direction:
            path_square = self.board.squares[square]
            if path_square.has_piece():
                if path_square.has_friendly_piece(piece):
                    break
                elif path_square.has_enemy_piece(piece):
                    moves.append(Move(start_square, path_square, moveNumber))
                    break
            else:
                moves.append(Move(start_square, path_square, moveNumber))


    def get_diagonal_moves(self, piece, moves, moveNumber):
        '''
        Finds the move-available squares in the up-right diagonal for 
        diagonally moving pieces.
        
        Finds valid-move squares above and right for diagonally moving pieces 
        (Bishops, Queens, and Kings).
        '''
        f, r = piece.get_coords()  # Coordinates of the piece.
        if piece.get_name() == 'King':
            file_range = rank_range = 2
        else:
            file_range = self.file_size
            rank_range = self.rank_size
        
        directions = dict(  # Make dictionary of the four diagonal directions.
            DOWNRIGHT = [
                (file, rank) 
                for file, rank in zip(
                    range(f + 1, f + file_range), 
                    range(r + 1, r + rank_range)
                ) 
                if (file < self.file_size and rank < self.rank_size)
            ],
            UPRIGHT = [
                (file, rank) 
                for file, rank in zip(
                    range(f + 1, f + file_range), 
                    reversed(range(r - rank_range, r))
                ) 
                if (file < self.file_size and rank >= 0)
            ],
            UPLEFT = [
                (file, rank) 
                for file, rank in zip(
                    reversed(range(f - file_range, f)),
                    reversed(range(r - rank_range, r))
                ) 
                if (file >= 0 and rank >= 0)
            ],
            DOWNLEFT = [
                (file, rank) 
                for file, rank in zip(
                    reversed(range(f - file_range, f)),
                    range(r + 1, r + rank_range)
                ) 
                if (file >= 0 and rank < self.rank_size)
            ],
        )
        
        for d in directions.values():
            self.find_moves_on_path(piece, d, moves, moveNumber)
    
            
    def get_file_moves(self, piece, moves, moveNumber):
        '''
        Get all movement-available squares above and below the piece.
        
        Finds valid move squares above row-moving pieces (Rooks, Queens, 
        and Kings).
        '''
        f, r = piece.get_coords()  # Coordinates of the piece.
        if piece.name == 'King':
            rank_range = 2
        else:
            rank_range = self.rank_size
        
        directions = dict(
            UP = [
                (f, rank) 
                for rank in reversed(range(r - rank_range, r))
                if rank >= 0
            ],
            DOWN = [
                (f, rank) 
                for rank in range(r + 1, r + rank_range)
                if rank < self.rank_size
            ]
        )
        for d in directions.values():
            self.find_moves_on_path(piece, d, moves, moveNumber)
    
    
    def get_rank_moves(self, piece, moves, moveNumber):
        '''
        Get all movement-available squares to the right of the piece.
        
        Finds valid move squares to the left and right of row-moving pieces
        (Rooks, Queens, and Kings).
        '''
        f, r = piece.get_coords()  # Coordinates of the piece.
        if piece.name == 'King':
            file_range = 2
        else:
            file_range = self.file_size
        
        directions = dict(
            RIGHT = [
                (file, r) 
                for file in range(f + 1, f + file_range)
                if file < self.file_size
            ],
            LEFT = [
                (file, r) 
                for file in reversed(range(f - file_range, f))
                if file >= 0
            ],
        )
        
        for d in directions.values():
            self.find_moves_on_path(piece, d, moves, moveNumber)
    

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
    board.squares[4, 7].set_piece(King('white'))
    board.squares[4, 0].set_piece(King('black'))
    
    
    board.update_pieces()
    
    return board


class Move():
    '''
    Object to store chess moves in.
    
    Moves will be stored in the move_log attribute of the GameState().
    '''
    
    def __init__(self, startSquare, endSquare, moveNumber):
        self.start_square = startSquare
        self.end_square = endSquare
        self.move_number = moveNumber
        self.piece_moved = self.start_square.get_piece()
        self.piece_captured = self.end_square.get_piece()
        self.move_id = (
            self.move_number,
            
            self.piece_moved,
            
            self.start_square.get_file() * 1000 
            + self.start_square.get_rank() * 100
            + self.end_square.get_file() * 10
            + self.end_square.get_rank() * 1,
            
            self.piece_captured
        )
        
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        
        return False
        
    def get_chess_notation(self):
        '''
        Returns the move in human-readable format.
        '''
        # TODO: Check if pieces of the same name are on the same rank as the 
        # piece moved in case more specific notation is needed.
        
        number = ''
        if self.piece_moved.get_color() == 'white':
            number = str(self.move_number + 1) + '. '
        
        if self.piece_moved.get_name() == 'Pawn':
            if self.piece_captured != None:
                return '{}{}{}{}'.format(
                    number,
                    self.start_square.get_name()[0],
                    'x',
                    self.end_square.get_name(),
                )
            
            return '{}{}'.format(number, self.end_square.get_name())
        
        else:
            spacer = ''
            if self.piece_captured != None:
                spacer = 'x'
            
            return "{}{}{}{}{}".format(
                number,
                self.piece_moved.get_symbol(), 
                self.start_square.get_name(),
                spacer, 
                self.end_square.get_name(),
            )
        









