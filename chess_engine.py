# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 22:29:53 2021

@author: Zach Chartrand

This is the engine that will run the chess game.
"""

from typing import Union, Tuple

from chess_pieces import Queen, Rook, Bishop, Knight
from chess_pieces import DIRECTIONS
from chess_board import makeStandardBoard, Square
# from chess_board import makeTwoRooksEndgameBoard, makeQueenEndgameBoard


class GameState():
    """
    This class is responsible for storing all the information about the
    current state of a chess game. It will also be responsible for
    determining the valid moves at the current state. It will also keep
    a move log.
    """
    
    def __init__(self):
        self.board = makeStandardBoard()
        self.file_size, self.rank_size = self.board.get_size()
        self.white_to_move = True
        self.move_log = []
        self.undo_log = []
        self.move_branches = []
        self.move_number = 0
        self.pins = []
        self.checks = []
        self.in_check = False
        self.gameover = False
        self.checkmate = False
        self.stalemate = False
        self.stalemate_counter = 0
        self.enpassant_coords = ()
        self.valid_moves = []
    
    def make_new_move(self, move):
        """
        Makes a new move outside of the moves in the move_log and
        undo_log.

        Saves the current branch of moves to the move_branches
        attribute, then clears the undo_log.
        """
        if self.undo_log:
            # Clear undo_log after new move if different from previous move.
            self.move_branches.append(self.undo_log)
            self.undo_log.clear()
        if (move.piece_moved.get_name() == 'Pawn'
                or move.piece_captured is not None):
            self.stalemate_counter = 0
        else:
            self.stalemate_counter += 1
        
        if move.name == '':
            move.name = move.get_chess_notation(self)

        self.make_move(move)

    def make_move(self, move):
        """
        Takes a Move as a parameter and executes the move.
        """
        pieces_set, pieces_removed = [], []
        if move.contains_enpassant():
            move.enpassant_square.remove_piece()
        elif move.piece_captured is not None:
            pieces_removed.append(move.piece_captured)
            move.end_square.remove_piece()
        move.start_square.remove_piece()
        if move.contains_promotion():
            move.end_square.set_piece(move.promotion_piece)
            pieces_set.append(move.promotion_piece)
            pieces_removed.append(move.piece_moved)
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
                self.enpassant_coords = move.piece_moved.get_coords()
            elif (self.enpassant_coords
                  or move.piece_moved.get_name() != "Pawn"):
                self.enpassant_coords = ()
        else:
            if self.enpassant_coords:
                self.enpassant_coords = ()

        self.white_to_move = not self.white_to_move
        self.move_number += 1
        self.board.update_pieces(pieces_set, pieces_removed)
    
    def undo_move(self):
        """Method to undo a chess move."""
        if self.move_log:
            pieces_set, pieces_removed = [], []
            move, stalemate_counter = self.move_log.pop()
            move.end_square.remove_piece()
            move.start_square.set_piece(move.piece_moved)
            if move.piece_captured is not None:
                pieces_set.append(move.piece_captured)
                if move.contains_enpassant():
                    move.enpassant_square.set_piece(move.piece_captured)
                else:
                    move.end_square.set_piece(move.piece_captured)
            if move == move.piece_moved.get_first_move():
                move.piece_moved.first_move = None
            if move.contains_castle():
                rook, rookStartSquare, rookEndSquare = move.castle
                rookEndSquare.remove_piece()
                rookStartSquare.set_piece(rook)
            if move.contains_promotion():
                pieces_removed.append(move.promotion_piece)
            if self.move_log:  # Needed to prevent AI bugs.
                previousMove, _ = self.move_log.copy().pop()
                if (previousMove.piece_moved.get_name() == 'Pawn'
                        and (abs(previousMove.end_square.get_rank()
                             - previousMove.start_square.get_rank()) == 2)):
                    self.enpassant_coords = (
                        (previousMove.end_square.get_coords())
                    )
                else:
                    self.enpassant_coords = ()

            if self.checkmate:
                self.checkmate = False
            if self.stalemate:
                self.stalemate = False
            self.white_to_move = not self.white_to_move
            self.move_number -= 1
            self.undo_log.append((move, stalemate_counter))
            self.board.update_pieces(pieces_set, pieces_removed)

    def redo_move(self):
        """Redo a previously undone move."""
        if self.undo_log:
            move, _ = self.undo_log.pop()
            self.make_move(move)

    def get_valid_moves(self):
        """
        Get all moves considering checks.

        1. Get the King from the side moving this turn.
        2. Figure out if the King is in check, and if so, by how many
           pieces.
        3. Remove all moves that put the King into check.
        4. If the King hasn't moved, find all castling moves and
        determine if they are valid.
        """
        moves = []
        if self.white_to_move:
            king = self.board.white_king
        else:
            king = self.board.black_king
        if king.get_square() is None:
            return []
        self.pins, self.checks = self.get_pins_and_checks(king)
# =============================================================================
#         # Lines for debugging pins and checks.
#         if self.pins:
#             for pin in self.pins:
#                 print('Pin on {}'.format(
#                     pin[0].get_piece().get_fullname()
#                 ))
#         if self.checks:
#             for check in self.checks:
#                 print('Check from {}'.format(
#                     check[0].get_piece().get_fullname()
#                 ))
# =============================================================================
        s = self.board.squares
        kingFile, kingRank = king.get_coords()
        if self.checks:
            self.in_check = True
            if len(self.checks) == 1:  # Only 1 check, block check or move away.
                moves = self.get_all_moves()
                # To block a check you must move a piece into one of the squares
                # between the enemy piece and the king.
                check = self.checks[0]
                # Get coordinates of the piece checking the King
                checkSquare, checkDirection = check
                pieceChecking = checkSquare.get_piece()
                
                validSquares = []  # Squares that pieces can move to.
                if pieceChecking.get_name() == 'Knight':
                    validSquares = [checkSquare]
                else:
                    for x, y in zip(range(self.file_size),
                        range(self.rank_size)):
                        endFile, endRank = (kingFile + checkDirection[0]*x,
                            kingRank + checkDirection[1]*y)
                        if (0 <= endFile < self.file_size
                                and 0 <= endRank < self.rank_size):
                            validSquare = s[(endFile, endRank)]
                            validSquares.append(validSquare)
                            if validSquare == checkSquare:
                                break
                # Iterate through reversed copy of the list.
                for move in reversed(moves):
                    if move.piece_moved.get_name() != 'King':
                        # Move doesn't move King so it must block or capture.
                        if move.end_square not in validSquares:
                        # i.e. if move doesn't block or capture.
                            moves.remove(move)

            else:  # Double check, so has to move.
                self.get_king_and_knight_moves(king, moves)

        else:  # Not in check, so all moves (outside of pins) are fine.
            self.in_check = False
            moves = self.get_all_moves()

        # Remove all moves that put the King in check.
        if moves:
            # print(len(moves))  # Debugging
            for move in reversed(moves):
                # print('Checking move to {}'.format(move.end_square.get_name()))
                if move.piece_moved.get_name() == 'King':
                    # If the move puts the King in check, remove that move
                    # from the valid moves list.
                    if self.get_pins_and_checks(king, move.end_square)[1]:
                        # print('Move goes into check: {}'.format(
                        #    move.end_square.get_name()))
                        moves.remove(move)
                        # print(len(moves))

        if not king.has_moved() and not self.in_check:
            self.get_castle_moves(king, moves)
            # Remove all moves that put the King in check.
            for move in reversed(moves):
                # print('Checking move to {}'.format(move.end_square.get_name()))
                if move.piece_moved.get_name() == 'King':
                    if self.get_pins_and_checks(king, move.end_square)[1]:
                        moves.remove(move)
                        # print(len(moves))
        
        # for move in moves:  # Debugging
        #     print(move.piece_moved.get_fullname(), move.end_square.get_name())
            
        return moves

    def get_castle_moves(self, king, moves):
        """Adds castling moves to valid moves."""
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
                                                kingSquare, 
                                                castleSquare,
                                                self.move_number,
                                                castle=(piece,
                                                piece.get_square(),rookSquare)
                                                ))
                                else:
                                    break

    def get_all_moves(self):
        """Get all moves without considering checks."""
        moves = []
        for piece in self.board.get_pieces():
            if piece.is_on_board():  # Needed for AI to work properly.
                # BUG: AI somehow still tries to make moves where the
                # start square has no piece.
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
                    elif name in ('King', 'Knight'):
                        self.get_king_and_knight_moves(piece, moves)
                    else:
                        self.find_moves_on_path(piece, moves)

        return moves

    def is_piece_pinned(self, piece):
        """Checks if the piece is pinned to the King in any direction."""
        if piece.get_name() != 'King':
            piece.pin_direction = ()
            for pin in reversed(self.pins):
                if pin[0] == piece.get_square():
                    piece.pin_direction = pin[1]
                    self.pins.remove(pin)
                    break

    def get_pawn_moves(self, pawn, moves):
        """
        Gets all possible moves for the Pawn.

        Allows for double move on beginning rank, forward movement
        unless obstructed by a piece, and diagonal capture.
        """
        board = self.board
        s = board.squares
        f, r = pawn.get_coords()
        startSquare = s[f, r]
        y = pawn.get_directions()[1]

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
                    and not s[f, r + 2*y].has_piece()
                ):
                    moves.append(Move(startSquare, s[f, r + 2*y],
                        self.move_number))

        # Captures
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

        # En passant
        if (self.enpassant_coords != ()
                and abs(f - self.enpassant_coords[0]) == 1
                and r == self.enpassant_coords[1]):
            epSquare = s[self.enpassant_coords]
            endSquare = s[self.enpassant_coords[0], r+y]
            move = Move(
                startSquare, endSquare, self.move_number,
                enpassantSquare=epSquare
            )
            move.piece_captured = epSquare.get_piece()
            moves.append(move)

    def get_king_and_knight_moves(self, piece, moves):
        """
        Generate moves for the King and Knight pieces.

        The King moves only one space in any direction, so there's no
        need to check for squares on a path.

        The Knight is the only piece that can jump, so the only thing
        this needs to do is check the, at most, eight (8) squares that
        it could move to and see if a friendly piece is there.  The
        Knight moves in an L shape: 2 squares in one direction, and 1
        move to the side.
        """
        if piece.is_on_board():  # Possible fix to AI bug.
            if not piece.is_pinned():
                f, r = piece.get_coords()
                s = self.board.squares
                for x, y in piece.get_directions():
                    endFile, endRank = f+x, r+y
                    if (
                        (0 <= endFile < self.file_size)
                        and (0 <= endRank < self.rank_size)
                    ):
                        if not s[endFile, endRank].has_friendly_piece(piece):
                            if piece.get_coords() != s[f, r].get_coords():
                                print(f'Piece square: {piece.get_coords()}')
                                print(f'Move square: {s[f, r].get_coords()}')
                            moves.append(
                                Move(s[f, r], s[endFile, endRank],
                                     self.move_number)
                            )

    def find_moves_on_path(self, piece, moves):
        """
        Finds all squares along a horizontal, vertical, or diagonal
        path and adds them to the move list.
        """
        if piece.is_on_board():
            start_square = piece.get_square()
            f, r = start_square.get_coords()
            if self.file_size >= self.rank_size:
                pathRange = self.file_size
            else:
                pathRange = self.rank_size
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
                                    moves.append(Move(
                                        start_square, path_square,
                                        self.move_number
                                        ))
                                    break
                            else:
                                moves.append(
                                    Move(start_square, path_square,
                                         self.move_number)
                                )

    def get_pins_and_checks(self, king, king_end_square=None):
        """Finds all pinned pieces and checks."""
        pins = []
        checks = []
        if king_end_square is None:
            kingFile, kingRank = king.get_square().get_coords()
        else:
            kingFile, kingRank = king_end_square.get_coords()
        # Check outward from king for pins and checks, keep track of pins.
        directions = (  # Make a tuple of all directions away from King.
            DIRECTIONS['HORIZONTAL']
            + DIRECTIONS['VERTICAL']
            + DIRECTIONS['DIAGONAL']
        )
        
        for x, y in directions:
            possiblePin = ()  # Reset possible pins
            for i, j in zip(range(1, self.file_size),
                range(1, self.rank_size)):
                (endFile, endRank) = (kingFile + x*i, kingRank + y*j)
                if ((0 <= endFile < self.file_size)
                    and (0 <= endRank < self.rank_size)):
                    square = self.board.squares[endFile, endRank]
                    if square.has_friendly_piece(king):
                        # First ally piece could be pinned.
                        piece = square.get_piece()
                        if piece is not king:
                            if not possiblePin:
                                possiblePin = (square, (x, y))
                            else:
                                # No need to check beyond second ally piece,
                                # as these will break the pin.
                                possiblePin = ()
                                break
                    elif square.has_enemy_piece(king):
                        piece = square.get_piece()
                        name = piece.get_name()
                        color = square.get_piece().get_color()
                        # Three possibilities in this complex conditional:
                        # 1. Any direction one square away and the piece
                        #    is a King (to prevent kings from attacking
                        #    each other.
                        # 2. One square away diagonally from the king and
                        #    the piece is a Pawn.
                        # 3. Is any other piece and the King is in one of the 
                        #    directions that that piece can move in.
                        
                        if (
                            (name, i, j) == ('King', 1, 1)
                             or (name == 'Pawn' 
                                     and ((color == 'black'
                                           and (x, y) in ((1, -1), (-1, -1)) 
                                           and j == 1)
                                     or (color == 'white' 
                                         and (x, y) in ((1, 1), (-1, 1)) 
                                         and j == 1)))
                            or (name not in ('King', 'Pawn')
                                and (x, y) in piece.get_directions())
                        ):
                            # print('Possible pin: {}'.format(possiblePin))
                            if not possiblePin:  # No piece blocking the King.
                                checks.append((square, (x, y)))
                                # print('Check appended: {}'.format(
                                #    square.get_name()))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:  # Enemy piece is not applying check.
                            # print(piece.get_fullname())
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
                    checks.append((square, (x, y)))

        return pins, checks

    def promote(self, choice, move):
        """Promotes Pawn to Queen, Knight, Rook, or Bishop."""
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

    def find_mate(self, validMoves):
        """
        Determines if the game is over
        and whether it is checkmate or stalemate.
        """
        if not validMoves:
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        elif self.stalemate_counter > 100:
            self.stalemate = True

        self.gameover = True if self.checkmate or self.stalemate else False


class Move():
    """
    Object to store chess moves in.

    Moves will be stored in the move_log attribute of the GameState().
    """

    def __init__(self, startSquare: Square, endSquare: Square, moveNumber: int,
            castle: Tuple[Union[Rook, Square]]=(),
            enpassantSquare: Union[Square, None]=None):
        if not startSquare.has_piece():
            raise ValueError('Square {} has no piece to move.'.format(
                startSquare.get_name()))
        else:
            self.start_square = startSquare
        self.end_square = endSquare
        self.move_number = moveNumber
        self.piece_moved = self.start_square.get_piece()
        self.enpassant_square = enpassantSquare
        self.piece_captured = self.end_square.get_piece()
        self.promotion_piece = None
        self.castle = castle  # Format (Rook piece, Rook end square)
        self.id = (
            self.move_number,

            id(self.piece_moved),

            self.start_square.get_file() * 1000
            + self.start_square.get_rank() * 100
            + self.end_square.get_file() * 10
            + self.end_square.get_rank() * 1,

            id(self.piece_captured),
        )
        self.name = ''  # The name in algebraic notation needs the gamestate 
            # to figure out the full notation. Generated when a move is made.

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.id == other.id

        return False
    
    def __hash__(self):
        return hash(self.id)

    def get_chess_notation(self, gs: GameState):
        """
        Returns the move in algebraic notation.
        """
        # TODO: Check if pieces of the same name are on the same rank as the
        # piece moved in case more specific notation is needed.
        if self.contains_castle():
            rookFile = self.castle[1].get_coords()[0]
            kingFile = self.start_square.get_coords()[0]
            if rookFile < kingFile:
                return 'O-O-O'
            else:
                return 'O-O'
        
        else:
            piece_moved = self.piece_moved
            name = piece_moved.get_name()
            spacer = ''
            startSquare = self.start_square
            endSquare = self.end_square
            
            if name == 'Pawn':
                startFile = ''
                promoSymbol, ep = '', ''
                if self.piece_captured is not None:
                    startFile = startSquare.get_name()[0]
                    spacer = 'x'
                    if self.contains_enpassant():
                        ep = ' e.p.'
                if self.contains_promotion():
                    promoSymbol = '=' + self.promotion_piece.get_symbol()

                return ''.join([
                        startFile,
                        spacer,
                        endSquare.get_name(),
                        promoSymbol,
                        ep,
                    ])

            else:
                symbol = piece_moved.get_symbol()
                startSquareName = ''
                if name != 'King':
                    color = piece_moved.get_color()
                    pieceList = gs.board.piece_lists[name][color]
                    if len(pieceList) > 1:
                        file, rank = '', ''
                        for piece in pieceList:
                            if file and rank:
                                break
                            if piece is not piece_moved:
                                for move in gs.valid_moves:
                                    if (move.end_square is endSquare
                                            and move.piece_moved is piece):
                                        startFile, startRank = (
                                            startSquare.get_name()[0],
                                            startSquare.get_name()[1]
                                        )
                                        otherFile, otherRank = (
                                            move.start_square.get_name()[0],
                                            move.start_square.get_name()[1]
                                        )
                                        if (startFile != otherFile 
                                                and not file):
                                            file = startFile
                                        elif (startRank != otherRank
                                                and not rank):
                                            rank = startRank
                        
                        startSquareName = ''.join([file, rank])
                    
                    
                if self.piece_captured is not None:
                    spacer = 'x'

                return ''.join([
                    symbol,
                    startSquareName,
                    spacer,
                    endSquare.get_name(),
                ])

    def __str__(self):
        number = str(self.move_number//2 + 1)
        if self.piece_moved.get_color() == 'black':
            spacer = '...'
        else:
            spacer = '. '
        
        return ''.join([number, spacer, self.name])

    def contains_promotion(self):
        """Returns whether or not a promotion occured during this move."""
        if self.promotion_piece is not None:
            return True

        return False

    def contains_castle(self):
        if self.castle:
            return True

        return False

    def contains_enpassant(self):
        if self.enpassant_square is not None:
            return True

        return False
