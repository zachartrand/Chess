# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 22:29:53 2021

@author: Zach Chartrand

This is the engine that will run the chess game.
"""

# import numpy as np

from chess_pieces import King, Queen, Rook, Bishop, Knight, Pawn
from chess_pieces import DIRECTIONS
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
        self.pins = []
        self.checks = []
        self.in_check = False
        self.checkmate = False
        self.stalemate = False
        self.stalemate_counter = 0
        self.enpassant = False
        
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
        if move.piece_moved.get_name() == 'Pawn':
            self.stalemate_counter = 0
        elif move.piece_captured != None:
            self.stalemate_counter = 0
        else:
            self.stalemate_counter += 1
        
        self.make_move(move)
    
    def make_move(self, move):
        '''
        Takes a Move as a parameter and executes the move.
        
        Does not work for castling, en passant, or pawn promotion.
        '''
        if move.contains_enpassant():
            move.piece_captured = move.enpassant_square.get_piece()
            move.enpassant_square.remove_piece()
        elif move.piece_captured != None:
            move.end_square.remove_piece()
        move.start_square.remove_piece()
        if move.contains_promotion():
            move.end_square.set_piece(move.promotion_piece)
        elif move.contains_castle():
            rook, rookStartSquare, rookEndSquare = move.castle
            rookStartSquare.remove_piece()
            rookEndSquare.set_piece(rook)
            move.end_square.set_piece(move.piece_moved)
        else:
            move.end_square.set_piece(move.piece_moved)
        
        self.move_log.append((move, self.stalemate_counter))
        if not move.piece_moved.has_moved():
            move.piece_moved.first_move = move
            if (move.piece_moved.get_name() == 'Pawn'
                and (abs(move.end_square.get_rank() 
                         - move.start_square.get_rank()) == 2)):
                self.enpassant = True
            elif self.enpassant:
                self.enpassant = False
        
        self.white_to_move = not self.white_to_move
        if self.white_to_move:
            self.move_number += 1
        self.board.update_pieces()
        
        # For debugging moves.
        print(move.get_chess_notation(), end=' ')
    
    def undo_move(self):
        '''Method to undo a chess move.'''
        if len(self.move_log) != 0:
            move, stalemate_counter = self.move_log.pop()
            if stalemate_counter > 0:
                self.stalemate_counter = stalemate_counter - 1
            move.end_square.remove_piece()
            move.start_square.set_piece(move.piece_moved)
            if move.piece_captured != None:
                if move.contains_enpassant():
                    move.enpassant_square.set_piece(move.piece_captured)
                    self.enpassant = True
                else:
                    move.end_square.set_piece(move.piece_captured)
                    self.enpassant = False
            if move == move.piece_moved.get_first_move():
                move.piece_moved.first_move = None
            if move.contains_castle():
                rook, rookStartSquare, rookEndSquare = move.castle
                rookEndSquare.remove_piece()
                rookStartSquare.set_piece(rook)
            
            self.white_to_move = not self.white_to_move
            if not self.white_to_move:
                self.move_number -= 1
            self.undo_log.append((move, stalemate_counter))
            self.board.update_pieces()
            
            # For debugging.
            print('Undid {}'.format(move.get_chess_notation()), end=' ')  
        
    def redo_move(self):
        '''Redo a previously undone move.'''
        if len(self.undo_log) != 0:
            move, _ = self.undo_log.pop()
            # For debugging.
            print('Redid ', end='')
            self.make_move(move)
            
            
        
    def get_valid_moves(self):
        '''
        Get all moves considering checks.
        
        1. Get the King from the side moving this turn.
        2. Figure out if the King is in check, and if so, by how many pieces.
        3. Remove all moves that put the King into check.
        4. If the King hasn't moved, find all castling moves and determine if 
           they are valid.
        '''
        moves = []
        if self.white_to_move:
            king = self.board.white_king
        else:
            king = self.board.black_king
        self.in_check, self.pins, self.checks = ( 
            self.get_pins_and_checks(king)
        )
# =============================================================================
#         if len(self.pins) != 0:
#             for pin in self.pins:
#                 print('Pin on {}'.format(
#                     pin[0].get_piece().get_fullname()
#                     ))
#         if len(self.checks) != 0:
#             for check in self.checks:
#                 print('Check from {}'.format(
#                     check[0].get_piece().get_fullname()
#                     ))
# =============================================================================
        s = self.board.squares
        kingFile, kingRank = king.get_coords()
        if self.in_check:
            if len(self.checks) == 1:  # Only 1 check, block check or move away.
                moves = self.get_all_moves()
                # To block a check you must move a piece into one of the squares
                # between the enemy piece and the king.
                check = self.checks[0]
                # Get coordinates of the piece checking the King
                checkSquare = check[0]
                checkDirection = check[1]
                pieceChecking = checkSquare.get_piece()
                
                validSquares = []  # Squares that pieces can move to.
                if pieceChecking.get_name() == 'Knight':
                    validSquares = [checkSquare]
                else:
                    for x, y in zip(range(self.file_size), 
                        range(self.rank_size)):
                        endFile, endRank = (kingFile + checkDirection[0] * x, 
                            kingRank + checkDirection[1] * y)
                        if (0 <= endFile < self.file_size 
                            and 0 <= endRank < self.rank_size):
                            validSquare = s[(endFile, endRank)]
                            validSquares.append(validSquare)
                            if validSquare == checkSquare:
                                break
                
                # When iterating through a list and removing items, iterate
                # backwards.
                for move in reversed(moves):
                    if move.piece_moved.get_name() != 'King':
                        # Move doesn't move King so it must block or capture.
                        if not (move.end_square in validSquares):
                        # i.e. if move doesn't block or capture.
                            moves.remove(move)
                
            else:  # Double check, so has to move.
                moves = self.move_functions['King'](king)
                    
        else:  # Not in check, so all moves (outside of pins) are fine.
            moves = self.get_all_moves()
            
        # Remove all moves that put the King in check.
        for move in reversed(moves):
            if move.piece_moved.get_name() == 'King':
                # If the move puts the King in check, remove that move from the
                # valid moves list.
                if self.get_pins_and_checks(king, move.end_square)[0]:
                    moves.remove(move)
        
        if not king.has_moved() and not self.in_check:
            self.get_castle_moves(king, moves)
            # Remove all moves that put the King in check.
            for move in reversed(moves):
                if move.piece_moved.get_name() == 'King':
                    if self.get_pins_and_checks(king, move.end_square)[0]:
                        moves.remove(move)
            
                    
        
        return moves
    
    def get_castle_moves(self, king, moves):
        '''Adds castling moves to valid moves.'''
        s = self.board.squares
        kingFile, kingRank = king.get_coords()
        kingSquare = king.get_square()
        for move in moves:
            if move.piece_moved.get_name() == 'King':
                # Look to the left and right of the King for potential 
                # castling squares.
                for x, _ in DIRECTIONS['HORIZONTAL']:
                    rookSquare = s[kingFile + x, kingRank]
                    # If the king can't move to the first square to the 
                    # side, he can't castle, move on to the next direction.
                    if rookSquare == move.end_square:
                        castleFile = kingFile + x * 2
                        castleSquare = s[castleFile, kingRank]
                        # Make sure the square is unoccupied.
                        if not castleSquare.has_piece():
                            # Make sure path to rook is empty.
                            for i in range(3, self.file_size):
                                newFile = kingFile + x * i
                                # Check if the square is on the board.
                                if 0 <= newFile < self.file_size:
                                    pathSquare = s[newFile, kingRank]
                                    if pathSquare.has_piece():
                                        piece = pathSquare.get_piece()
                                        if (pathSquare.has_enemy_piece(king)
                                            or piece.get_name() != 'Rook'):
                                            break
                                        elif (piece.get_name() == 'Rook'
                                              and not piece.has_moved()):
                                            moves.append(Move(
                                                kingSquare, castleSquare,
                                                self.move_number,
                                                castle=(piece, 
                                                piece.get_square(),rookSquare)
                                                ))
                                else:
                                    break
            
        
        
        
    def get_all_moves(self):
        '''Get all moves without considering checks.'''
        moves = []
        for piece in self.board.get_pieces():
            turn = piece.get_color()
            name = piece.get_name()
            if (
                (turn == 'white' and self.white_to_move)
                or (turn == 'black' and not self.white_to_move)
            ):
                # Find pins and flag pieces.
                if name != 'King':
                    self.is_piece_pinned(piece)
                # Get moves for each piece.
                if name == 'Pawn':
                    self.get_pawn_moves(piece, moves)
                elif name == 'Knight':
                    self.get_knight_moves(piece, moves)
                else:
                    self.find_moves_on_path(piece, moves)
                # for func in self.move_functions[name]:
                #     func(piece, moves)
        
        return moves
    
    def is_piece_pinned(self, piece):
        piece.pin_direction = ()
        for pin in reversed(self.pins):
            if pin[0] == piece.get_square():
                piece.pin_direction = pin[1]
                self.pins.remove(pin)
                break
                
    
    def get_pawn_moves(self, pawn, moves):
        '''
        Gets all possible moves for the Pawn.
        
        Allows for double move on beginning rank, forward movement unless 
        obstructed by a piece, and diagonal capture.
        '''
        s = self.board.squares
        f, r = pawn.get_coords()
        startSquare = s[f, r]
        y = pawn.get_directions()[1]
        enpassantRank = pawn.get_promotion_rank() - y * 3
        
        # Vertical moves
        if (not pawn.is_pinned() 
            or pawn.get_pin_direction() == (0, y)
            or pawn.get_pin_direction() == (0, -y)):
            if (r + y < self.rank_size 
                and not s[f, r + y].has_piece()):
                moves.append(Move(startSquare, s[f, r + y],
                        self.move_number))
                # Double move on first turn.
                if (
                    (not pawn.has_moved()) 
                    and not s[f, r + 2 * y].has_piece()
                ):
                    moves.append(Move(startSquare, s[f, r + 2 * y],
                        self.move_number))
                    
        for x, _ in DIRECTIONS['HORIZONTAL']:
            if (not pawn.is_pinned()
                or pawn.get_pin_direction() == (x, y)):
                if ((0 <= f+x < self.file_size) 
                    and (0 <= r+y < self.rank_size)):
                    captureSquare = s[f+x, r+y]
                    if (captureSquare.has_piece() 
                        and captureSquare.has_enemy_piece(pawn)):
                        moves.append(Move(startSquare, captureSquare,
                                          self.move_number))
        
        if self.enpassant and r == enpassantRank:
            for x, _ in DIRECTIONS['HORIZONTAL']:
                sideSquare = s[f+x, r]
                piece = sideSquare.get_piece()
                if piece != None:
                    moveNumber = piece.first_move.move_number
                    if (piece.get_name() == 'Pawn'
                        and piece.get_first_move().end_square == sideSquare
                        and ((self.white_to_move 
                              and self.move_number - 1 == moveNumber) 
                             or (not self.white_to_move 
                                 and self.move_number == moveNumber))):
                        endSquare = s[f+x, r+y]
                        moves.append(Move(
                                startSquare, endSquare, self.move_number,
                                enpassantSquare=sideSquare
                                ))
                    
            
    def get_knight_moves(self, knight, moves):
        '''
        Generate moves for the Knight piece.
        
        The Knight is the only piece that can jump, so the only thing this needs 
        to do is check the, at most, eight (8) squares that it could move to and 
        see if a friendly piece is there.  The Knight moves in an L shape: 2 
        squares in one direction, and 1 move to the side.
        '''
        if not knight.is_pinned():
            f, r = knight.get_coords()
            s = self.board.squares
            for x, y in knight.get_directions():
                endFile, endRank = f+x, r+y
                if (
                    (0 <= endFile < self.file_size) 
                    and (0 <= endRank < self.rank_size)
                ):
                    if not s[endFile, endRank].has_friendly_piece(knight):
                        moves.append(
                            Move(s[f, r], s[endFile, endRank], self.move_number)
                        )
    
    def find_moves_on_path(self, piece, moves):
        '''
        Finds all squares along a horizontal, vertical, or diagonal path and 
        adds them to the move list.
        '''
        if piece.get_range() != None:
            if piece.get_range() == 'inf':
                if self.file_size >= self.rank_size:
                    pathRange = self.file_size
                else:
                    pathRange = self.rank_size
            else:
                pathRange = 1 + piece.get_range()
                
            start_square = piece.get_square()
            f, r = start_square.get_coords()
            for direction in piece.get_directions():
                x, y = direction
                if (not piece.is_pinned() 
                    or piece.get_pin_direction() == direction
                    or piece.get_pin_direction() == (-x, -y)):
                    for i in range(1, pathRange):
                        file, rank = f + x*i, r + y*i
                        if (0 <= file < self.file_size
                            and 0 <= rank < self.rank_size):
                            path_square = self.board.squares[file, rank]
                            if path_square.has_piece():
                                if path_square.has_friendly_piece(piece):
                                    break
                                elif path_square.has_enemy_piece(piece):
                                    moves.append(Move(start_square, path_square,
                                        self.move_number))
                                    break
                            else:
                                moves.append(Move(start_square, path_square,
                                                  self.move_number))
                            
        else:
            raise TypeError("This piece doesn't move along a path.")
    
    def get_pins_and_checks(self, king, king_end_square=None):
        '''Finds all pinned pieces and checks.'''
        pins = []
        checks = []
        inCheck = False
        if king_end_square == None:
            kingFile, kingRank = king.get_square().get_coords()
        else:
            kingFile, kingRank = king_end_square.get_coords()
        # Check outward from king for pins and checks, keep track of pins.
        directions = dict(  # Make a tuple of all directions away from King.
            straight = (
                (-1, 0),  # Left
                (0, -1),  # Up
                (1, 0),   # Right
                (0, 1),   # Down
            ),
            diagonal = (
                (-1, -1), # Up Left
                (1, -1),  # Up Right
                (-1, 1),  # Down Left
                (1, 1),   # Down Right
            )
        )   
            
        
        for type_ in directions:
            for x, y in directions[type_]:
                possiblePin = ()  # Reset possible pins
                for i, j in zip(range(1, self.file_size), 
                    range(1, self.rank_size)):
                    (endFile, endRank) = (kingFile + x*i, kingRank + y*j)
                    if ((0 <= endFile < self.file_size)
                        and (0 <= endRank < self.rank_size)):
                        square = self.board.squares[endFile, endRank]
                        if square.has_friendly_piece(king):
                            # First ally piece could be pinned.
                            if possiblePin == ():
                                possiblePin = (square, (x, y))
                            else:
                                # No need to check beyond second ally piece,
                                # as these will break the pin.
                                possiblePin = ()
                                break
                        elif square.has_enemy_piece(king):
                            name = square.get_piece().get_name()
                            color = square.get_piece().get_color()
                            # Five possibilities in this complex conditional:
                            # 1. In a cardinal direction away from the king 
                            #    and the piece is a Rook.
                            # 2. Diagonally away from the king and the piece 
                            #    is a Bishop.
                            # 3. One square away diagonally from the king and
                            #    the piece is a Pawn.
                            # 4. Any direction and the piece is a queen.
                            # 5. Any direction one square away and the piece
                            #    is a King (to prevent kings from attacking 
                            #    each other).
                            if ((type_ == 'straight' and name == 'Rook')
                                or (type_ == 'diagonal' and name == 'Bishop')
                                or (name == 'Queen')
                                or (i == 1 and j == 1 and name == 'King')
                                or (name == 'Pawn' and j == 1 
                                    and color == 'black'
                                    and ((x, y) == directions['diagonal'][0] 
                                         or (x, y) == directions['diagonal'][1]))
                                or (name == 'Pawn' and j == 1 
                                    and color == 'white' 
                                    and ((x, y) == directions['diagonal'][2] 
                                        or (x, y) == directions['diagonal'][3]))):
                                if possiblePin == ():  # No piece blocking the 
                                # King.
                                    inCheck = True
                                    checks.append((square, (x, y)))
                                    break
                                else:
                                    pins.append(possiblePin)
                                    break
                            else:  # Enemy piece is not applying check.
                                break
                    else:
                        break  # Off the board.
        # Now look for Knight checks.
        knightMoves = DIRECTIONS['KNIGHT']
        
        for x, y in knightMoves:
            endFile, endRank = kingFile + x, kingRank + y
            if (
                (0 <= endFile < self.file_size)
                and (0 <= endRank < self.rank_size)
            ):
                square = self.board.squares[endFile, endRank]
                if (
                    square.has_enemy_piece(king)
                    and square.get_piece().get_name() == 'Knight'
                ):
                    inCheck = True
                    checks.append((square, (x, y)))
        
        return inCheck, pins, checks
    
    def promote(self, choice, move):
        '''Promotes Pawn to Queen, Knight, Rook, or Bishop.'''
        if move.piece_moved.get_name() == 'Pawn':
            PROMOTION = dict(
                q = Queen,
                k = Knight,
                r = Rook,
                b = Bishop,
            )
            color = move.piece_moved.get_color()
            if choice in PROMOTION.keys():
                promotionPiece = PROMOTION[choice](color)
                move.promotion_piece = promotionPiece
        else:
            raise ValueError('Only Pawns can be promoted.')
    
    def findCheckmateOrStalemate(self, validMoves):
        if len(validMoves) == 0:
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        elif self.stalemate_counter > 100:
            self.stalemate = True


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


class Move():
    '''
    Object to store chess moves in.
    
    Moves will be stored in the move_log attribute of the GameState().
    '''
    
    def __init__(self, startSquare, endSquare, moveNumber, 
                 promotion=None, castle=(), enpassantSquare=None):
        self.start_square = startSquare
        self.end_square = endSquare
        self.move_number = moveNumber
        self.piece_moved = self.start_square.get_piece()
        self.piece_captured = self.end_square.get_piece()
        self.promotion_piece = None
        self.castle = castle # Format (Rook piece, Rook end square)
        self.enpassant_square = enpassantSquare
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
        
        number, spacer = '', ''
        startSquare = self.start_square.get_name()
        endSquare = self.end_square.get_name()
        if self.contains_castle():
            rookFile = self.castle[1].get_coords()[0]
            kingFile = self.start_square.get_coords()[0]
            if rookFile < kingFile:
                return 'O-O-O'
            else:
                return 'O-O'
        else:
            if self.piece_moved.get_color() == 'white':
                number = str(self.move_number + 1) + '. '
            
            if self.piece_moved.get_name() == 'Pawn':
                startFile, promoSymbol, ep = '', '', ''
                if self.contains_enpassant():
                    startFile = startSquare[0]
                    ep = 'e.p.'
                    spacer = 'x'
                elif self.piece_captured != None:
                    startFile = startSquare[0]
                    spacer = 'x'
                if self.contains_promotion():
                    promoSymbol = '=' + self.promotion_piece.get_symbol()
                
                return ''.join([
                        number,
                        startFile,
                        spacer,
                        endSquare,
                        promoSymbol,
                        ep,
                    ])
            
            else:
                symbol = self.piece_moved.get_symbol()
                if self.piece_captured != None:
                    spacer = 'x'
                
                return "{}{}{}{}{}".format(
                    number,
                    symbol, 
                    startSquare,
                    spacer, 
                    endSquare,
                )
        
    def contains_promotion(self):
        '''Returns whether or not a promotion occured during this move.'''
        if self.promotion_piece != None:
            return True
        
        return False
    
    def contains_castle(self):
        if len(self.castle) > 0:
            return True
        
        return False
    
    def contains_enpassant(self):
        if self.enpassant_square != None:
            return True
        
        return False
        









