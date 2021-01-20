from abc import ABC, abstractmethod

from src.utils import MoveNotAvailableError, Color, EmptyFieldError, States
# TODO: calculate_moves_available rework.
# TODO: save previous moves. Somehow...........
# TODO: calculate "potential" moves. Make a mappa


class Figure(ABC):
    type = None

    @classmethod
    def get_type(cls):
        return cls.type

    def __init__(self, x_position, y_position, color, game=None):
        self.game = game
        self.color = color
        self.current_position = (x_position, y_position)
        self.x_position = x_position
        self.y_position = y_position
        # self.moves_available = self.calculate_moves_available(chess_field=False)
        self.moves_available = []
        self.is_eaten = False
        self.type = self.get_type()
        self.moved = False

    def to_json(self):
        return {
            "color": self.color,
            "current_position": self.current_position,
            "x_position": self.x_position,
            "y_position": self.y_position,
            "moves_available": self.moves_available,
            "is_eaten": self.is_eaten,
            "type": self.type
        }

    def move(self, x_position, y_position):
        if (x_position, y_position) in self.moves_available:
            # Pawn transformation
            if self.type == 'pawn':
                if (self.color == Color.White.value and y_position == 0) \
                        or (self.color == Color.Black.value and y_position == 7):
                    self.game.chess_field[self.y_position][self.x_position] = None
                    new_figure = Queen(self.x_position, self.y_position, self.color, self.game)
                    self.game.chess_field[self.y_position][self.x_position] = new_figure
                    self.game.player_dict[self.color].figures_list.remove(self)
                    self.game.player_dict[self.color].figures_list.append(new_figure)
                    self.game.player_dict[self.color].figures_dict['pawns'].remove(self)
                    self.game.player_dict[self.color].figures_dict['pawns'].append(new_figure)
                    self = new_figure

            # Castling
            if self.type == 'king' \
                    and abs(self.x_position - x_position) == 2:
                if self.x_position - x_position > 0:  # Left castling
                    rook = self.game.chess_field[y_position][0]
                    rook_position = (x_position + 1, y_position)
                else:  # Right castling
                    rook = self.game.chess_field[y_position][7]
                    rook_position = (x_position - 1, y_position)
                rook.moved = True
                self.game.chess_field_update(rook, rook_position)
                rook.current_position = rook_position
                rook.x_position = rook_position[0]
                rook.y_position = rook_position[1]
                # rook.moves_available = rook.calculate_moves_available()
            self.moved = True
            self.game.chess_field_update(self, (x_position, y_position))
            self.current_position = (x_position, y_position)
            self.x_position = x_position
            self.y_position = y_position


            # self.moves_available = self.calculate_moves_available()
        else:
            raise MoveNotAvailableError('Figure cannot move here')
        for player in self.game.players:
            player.update_figures_moves(self)
            if player.is_king_attacked():
                player.king_attacked = True
            else:
                player.king_attacked = False

    @abstractmethod
    def calculate_moves_available(self, board, figures_dict, check_king=True):
        pass

    def check_check(self, moves, board, figures_dict):
        moves_to_delete = []
        for move in moves:
            # Temporary move
            old_position = (self.x_position, self.y_position)
            self.current_position = move
            self.x_position, self.y_position = move
            old_position_x, old_position_y = old_position
            new_position_x, new_position_y = move
            # chess_field[old_position_y][old_position_x], chess_field[new_position_y][new_position_x] = \
            #     chess_field[new_position_y][new_position_x], chess_field[old_position_y][old_position_x]
            board[old_position_y][old_position_x] = None
            figure_reserve = board[new_position_y][new_position_x]
            if figure_reserve is not None:
                figure_reserve.is_eaten = True
            board[new_position_y][new_position_x] = self

            #checking is king attacked
            is_king_attacked = False
            if self.color == Color.White.value:
                king_x, king_y = figures_dict['white_king'].current_position
            else:
                king_x, king_y = figures_dict['black_king'].current_position
            enemy_color = 'white' if self.color == 'black' else 'black'
            #knight checks
            if self.validity_test(king_x + 2, king_y + 1, board) and \
                    board[king_y + 1][king_x + 2] is not None and \
                    board[king_y + 1][king_x + 2].color == enemy_color and \
                    board[king_y + 1][king_x + 2].type == 'knight':
                is_king_attacked = True
            if self.validity_test(king_x + 2, king_y - 1, board) and \
                    board[king_y - 1][king_x + 2] is not None and \
                    board[king_y - 1][king_x + 2].color == enemy_color and \
                    board[king_y - 1][king_x + 2].type == 'knight':
                is_king_attacked = True
            if self.validity_test(king_x - 2, king_y + 1, board) and \
                    board[king_y + 1][king_x - 2] is not None and \
                    board[king_y + 1][king_x - 2].color == enemy_color and \
                    board[king_y + 1][king_x - 2].type == 'knight':
                is_king_attacked = True
            if self.validity_test(king_x - 2, king_y - 1, board) and \
                    board[king_y - 1][king_x - 2] is not None and \
                    board[king_y - 1][king_x - 2].color == enemy_color and \
                    board[king_y - 1][king_x - 2].type == 'knight':
                is_king_attacked = True
            if self.validity_test(king_x + 1, king_y + 2, board) and \
                    board[king_y + 2][king_x + 1] is not None and \
                    board[king_y + 2][king_x + 1].color == enemy_color and \
                    board[king_y + 2][king_x + 1].type == 'knight':
                is_king_attacked = True
            if self.validity_test(king_x + 1, king_y - 2, board) and \
                    board[king_y - 2][king_x + 1] is not None and \
                    board[king_y - 2][king_x + 1].color == enemy_color and \
                    board[king_y - 2][king_x + 1].type == 'knight':
                is_king_attacked = True
            if self.validity_test(king_x - 1, king_y + 2, board) and \
                    board[king_y + 2][king_x - 1] is not None and \
                    board[king_y + 2][king_x - 1].color == enemy_color and \
                    board[king_y + 2][king_x - 1].type == 'knight':
                is_king_attacked = True
            if self.validity_test(king_x - 1, king_y - 2, board) and \
                    board[king_y - 2][king_x - 1] is not None and \
                    board[king_y - 2][king_x - 1].color == enemy_color and \
                    board[king_y - 2][king_x - 1].type == 'knight':
                is_king_attacked = True

            # checking pawn
            if enemy_color == 'white':
                if self.validity_test(king_x - 1, king_y + 1, board) and \
                        board[king_y + 1][king_x - 1] is not None and \
                        board[king_y + 1][king_x - 1].color == enemy_color and \
                        board[king_y + 1][king_x - 1].type == 'pawn':
                    is_king_attacked = True
                if self.validity_test(king_x + 1, king_y + 1, board) and \
                        board[king_y + 1][king_x + 1] is not None and \
                        board[king_y + 1][king_x + 1].color == enemy_color and \
                        board[king_y + 1][king_x + 1].type == 'pawn':
                    is_king_attacked = True
            else:
                if self.validity_test(king_x - 1, king_y - 1, board) and \
                        board[king_y - 1][king_x - 1] is not None and \
                        board[king_y - 1][king_x - 1].color == enemy_color and \
                        board[king_y - 1][king_x - 1].type == 'pawn':
                    is_king_attacked = True
                if self.validity_test(king_x + 1, king_y - 1, board) and \
                        board[king_y - 1][king_x + 1] is not None and \
                        board[king_y - 1][king_x + 1].color == enemy_color and \
                        board[king_y - 1][king_x + 1].type == 'pawn':
                    is_king_attacked = True

            # checking rook
            # upwards
            x_index = king_x
            y_index = king_y - 1
            while self.validity_test(x_index, y_index, board):
                if board[y_index][x_index] is None:
                    y_index -= 1
                else:
                    if board[y_index][x_index].color == enemy_color and \
                            board[y_index][x_index].type in ('rook', 'queen'):
                        is_king_attacked = True
                    break
            # downwards
            x_index = king_x
            y_index = king_y + 1
            while self.validity_test(x_index, y_index, board):
                if board[y_index][x_index] is None:
                    y_index += 1
                else:
                    if board[y_index][x_index].color == enemy_color and \
                            board[y_index][x_index].type in ('rook', 'queen'):
                        is_king_attacked = True
                    break
            # left
            x_index = king_x - 1
            y_index = king_y
            while self.validity_test(x_index, y_index, board):
                if board[y_index][x_index] is None:
                    x_index -= 1
                else:
                    if board[y_index][x_index].color == enemy_color and \
                            board[y_index][x_index].type in ('rook', 'queen'):
                        is_king_attacked = True
                    break
            # right
            x_index = king_x + 1
            y_index = king_y
            while self.validity_test(x_index, y_index, board):
                if board[y_index][x_index] is None:
                    x_index += 1
                else:
                    if board[y_index][x_index].color == enemy_color and \
                            board[y_index][x_index].type in ('rook', 'queen'):
                        is_king_attacked = True
                    break

            # bishop
            # upright
            x_index = king_x + 1
            y_index = king_y - 1
            while self.validity_test(x_index, y_index, board):
                if board[y_index][x_index] is None:
                    x_index += 1
                    y_index -= 1
                else:
                    if board[y_index][x_index].color == enemy_color and \
                            board[y_index][x_index].type in ('bishop', 'queen'):
                        is_king_attacked = True
                    break
            # upleft
            x_index = king_x - 1
            y_index = king_y - 1
            while self.validity_test(x_index, y_index, board):
                if board[y_index][x_index] is None:
                    x_index -= 1
                    y_index -= 1
                else:
                    if board[y_index][x_index].color == enemy_color and \
                            board[y_index][x_index].type in ('bishop', 'queen'):
                        is_king_attacked = True
                    break
            # downright
            x_index = king_x + 1
            y_index = king_y + 1
            while self.validity_test(x_index, y_index, board):
                if board[y_index][x_index] is None:
                    x_index += 1
                    y_index += 1
                else:
                    if board[y_index][x_index].color == enemy_color and \
                            board[y_index][x_index].type in ('bishop', 'queen'):
                        is_king_attacked = True
                    break
            # downleft
            x_index = king_x - 1
            y_index = king_y + 1
            while self.validity_test(x_index, y_index, board):
                if board[y_index][x_index] is None:
                    x_index -= 1
                    y_index += 1
                else:
                    if board[y_index][x_index].color == enemy_color and \
                            board[y_index][x_index].type in ('bishop', 'queen'):
                        is_king_attacked = True
                    break

            #checking king
            if self.validity_test(king_x + 1, king_y + 1, board) and \
                    board[king_y + 1][king_x + 1] is not None and \
                    board[king_y + 1][king_x + 1].color == enemy_color and \
                    board[king_y + 1][king_x + 1].type == 'king':
                is_king_attacked = True
            elif self.validity_test(king_x + 1, king_y, board) and \
                    board[king_y][king_x + 1] is not None and \
                    board[king_y][king_x + 1].color == enemy_color and \
                    board[king_y][king_x + 1].type == 'king':
                is_king_attacked = True
            elif self.validity_test(king_x + 1, king_y - 1, board) and \
                    board[king_y - 1][king_x + 1] is not None and \
                    board[king_y - 1][king_x + 1].color == enemy_color and \
                    board[king_y - 1][king_x + 1].type == 'king':
                is_king_attacked = True
            elif self.validity_test(king_x, king_y + 1, board) and \
                    board[king_y + 1][king_x] is not None and \
                    board[king_y + 1][king_x].color == enemy_color and \
                    board[king_y + 1][king_x].type == 'king':
                is_king_attacked = True
            elif self.validity_test(king_x, king_y - 1, board) and \
                    board[king_y - 1][king_x] is not None and \
                    board[king_y - 1][king_x].color == enemy_color and \
                    board[king_y - 1][king_x].type == 'king':
                is_king_attacked = True
            elif self.validity_test(king_x - 1, king_y + 1, board) and \
                    board[king_y + 1][king_x - 1] is not None and \
                    board[king_y + 1][king_x - 1].color == enemy_color and \
                    board[king_y + 1][king_x - 1].type == 'king':
                is_king_attacked = True
            elif self.validity_test(king_x - 1, king_y, board) and \
                    board[king_y][king_x - 1] is not None and \
                    board[king_y][king_x - 1].color == enemy_color and \
                    board[king_y][king_x - 1].type == 'king':
                is_king_attacked = True
            elif self.validity_test(king_x - 1, king_y -1, board) and \
                    board[king_y - 1][king_x - 1] is not None and \
                    board[king_y - 1][king_x - 1].color == enemy_color and \
                    board[king_y - 1][king_x - 1].type == 'king':
                is_king_attacked = True
            if is_king_attacked:
                moves_to_delete.append(move)
            # Back to the old state
            # chess_field[old_position_y][old_position_x], chess_field[new_position_y][new_position_x] = \
            #     chess_field[new_position_y][new_position_x], chess_field[old_position_y][old_position_x]
            board[old_position_y][old_position_x] = self
            board[new_position_y][new_position_x] = figure_reserve
            if figure_reserve is not None:
                figure_reserve.is_eaten = False
            self.current_position = old_position
            self.x_position, self.y_position = old_position

        for move in moves_to_delete:
            moves.remove(move)
        return moves
    # def check_check(self, moves, board, figures_dict):
    #     moves_to_delete = []
    #     for move in moves:
    #         # Temporary move
    #         old_position = (self.x_position, self.y_position)
    #         self.current_position = move
    #         self.x_position, self.y_position = move
    #         old_position_x, old_position_y = old_position
    #         new_position_x, new_position_y = move
    #         # chess_field[old_position_y][old_position_x], chess_field[new_position_y][new_position_x] = \
    #         #     chess_field[new_position_y][new_position_x], chess_field[old_position_y][old_position_x]
    #         board[old_position_y][old_position_x] = None
    #         figure_reserve = board[new_position_y][new_position_x]
    #         if figure_reserve is not None:
    #             figure_reserve.is_eaten = True
    #         board[new_position_y][new_position_x] = self
    #         if self.color == Color.White.value:
    #             enemy_color = Color.Black.value
    #         else:
    #             enemy_color = Color.White.value
    #         backup_list = []
    #         for figure in figures_dict[enemy_color]:
    #             backup_list.append(figure.moves_available)
    #         self.game.player_dict[enemy_color].update_figures_moves(check_king=False)
    #
    #         # for figure in figures_dict[self.color]:
    #         #     if figure.type == 'king':
    #         #         king = figure
    #         #         break
    #
    #         if self.color == Color.White.value:
    #             for figure in figures_dict[Color.Black.value]:
    #                 if figures_dict['white_king'].current_position in figure.moves_available:
    #                     moves_to_delete.append(move)
    #                     break
    #         else:
    #             for figure in figures_dict[Color.White.value]:
    #                 if figures_dict['black_king'].current_position in figure.moves_available:
    #                     moves_to_delete.append(move)
    #                     break
    #         # Back to the old state
    #         # chess_field[old_position_y][old_position_x], chess_field[new_position_y][new_position_x] = \
    #         #     chess_field[new_position_y][new_position_x], chess_field[old_position_y][old_position_x]
    #         board[old_position_y][old_position_x] = self
    #         board[new_position_y][new_position_x] = figure_reserve
    #         if figure_reserve is not None:
    #             figure_reserve.is_eaten = False
    #         self.current_position = old_position
    #         self.x_position, self.y_position = old_position
    #
    #         for i, figure in enumerate(figures_dict[enemy_color]):
    #             figure.moves_available = backup_list[i]
    #
    #     for move in moves_to_delete:
    #         moves.remove(move)
    #     return moves

    def validity_test(self, x_position, y_position, board):
        try:
            if x_position < 0 or y_position < 0:
                return False
            elif board[y_position][x_position] is None or \
                    self.color != board[y_position][x_position].color:
                return True
            else:
                return False
        except IndexError:
            return False


class Pawn(Figure):
    type = 'pawn'
    sign = 'P'
    value_table_white = [
        [55,55,55,55,55,55,55,55],
        [5,5,5,5,5,5,5,5],
        [1,1,2,3,3,2,1,1],
        [0.5,0.5,1,2.5,2.5,1,0.5,0.5],
        [0,0,0,2,2,0,0,0],
        [0.5,-0.5,-1,0,0,-1,-0.5,0.5],
        [0.5,1,1,-2,-2,1,1,0.5],
        [0,0,0,0,0,0,0,0]
    ]
    # value_table_black = value_table_white[-1::-1]
    # value_table_black = list(reversed(value_table_white))
    value_table_black = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0.5, 1, 1, -2, -2, 1, 1, 0.5],
        [0.5, -0.5, -1, 0, 0, -1, -0.5, 0.5],
        [0, 0, 0, 2, 2, 0, 0, 0],
        [0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5],
        [1, 1, 2, 3, 3, 2, 1, 1],
        [5, 5, 5, 5, 5, 5, 5, 5],
        [55, 55, 55, 55, 55, 55, 55, 55],

    ]

    def calculate_moves_available(self, board, figures_dict, check_king=True):
        moves_available = []
        if self.color == Color.White.value:
            if self.y_position != 0:
                # Vertical move
                if board[self.y_position - 1][self.x_position] is None:
                    moves_available.append((self.x_position, self.y_position - 1))

                # Vertical two lines
                if self.y_position == self.game.y_length - 2 and \
                        board[self.y_position - 2][self.x_position] is None and \
                        board[self.y_position - 1][self.x_position] is None:
                    moves_available.append((self.x_position, self.y_position - 2))

                # Eating left
                if self.x_position != 0:
                    if board[self.y_position - 1][self.x_position - 1] is not None:
                        if self.color != board[self.y_position - 1][self.x_position - 1].color:
                            moves_available.append((self.x_position - 1, self.y_position - 1))

                # Eating right
                if self.x_position != self.game.x_length - 1:
                    if board[self.y_position - 1][self.x_position + 1] is not None:
                        if self.color != board[self.y_position - 1][self.x_position + 1].color:
                            moves_available.append((self.x_position + 1, self.y_position - 1))

        else:  # self.color = Color.Black.value
            if self.y_position != self.game.y_length - 1:
                # Vertical move
                if board[self.y_position + 1][self.x_position] is None:
                    moves_available.append((self.x_position, self.y_position + 1))

                # Vertical two lines
                if self.y_position == 1 and \
                        board[self.y_position + 2][self.x_position] is None and \
                        board[self.y_position + 1][self.x_position] is None:
                    moves_available.append((self.x_position, self.y_position + 2))

                # Eating left
                if self.x_position != 0:
                    if board[self.y_position + 1][self.x_position - 1] is not None:
                        if self.color != board[self.y_position + 1][self.x_position - 1].color:
                            moves_available.append((self.x_position - 1, self.y_position + 1))

                # Eating right
                if self.x_position != self.game.x_length - 1:
                    if board[self.y_position + 1][self.x_position + 1] is not None:
                        if self.color != board[self.y_position + 1][self.x_position + 1].color:
                            moves_available.append((self.x_position + 1, self.y_position + 1))

        if check_king:
            return self.check_check(moves_available, board, figures_dict)
        return moves_available

    def move(self, x_position, y_position):
        super().move(x_position, y_position)
        # TODO: add pawn transformation


class Rook(Figure):
    type = 'rook'
    sign = 'R'
    value_table_white = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0.5, 1, 1, 1, 1, 1, 1, 0.5],
        [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
        [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
        [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
        [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
        [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
        [0, 0, 0, 0.5, 0.5, 0, 0, 0],
    ]
    # value_table_black = value_table_white[-1::-1]
    value_table_black = list(reversed(value_table_white))

    def calculate_moves_available(self, board, figures_dict, check_king=True):
        moves_available = []
        # Downwards
        if self.y_position != self.game.y_length - 1:
            y_index = self.y_position + 1
            while y_index != self.game.y_length:
                if board[y_index][self.x_position] is None:
                    moves_available.append((self.x_position, y_index))
                    y_index += 1
                elif self.color != board[y_index][self.x_position].color:
                    moves_available.append((self.x_position, y_index))
                    break
                else:
                    break
        # Upwards
        if self.y_position != 0:
            y_index = self.y_position - 1
            while y_index != -1:
                if board[y_index][self.x_position] is None:
                    moves_available.append((self.x_position, y_index))
                    y_index -= 1
                elif self.color != board[y_index][self.x_position].color:
                    moves_available.append((self.x_position, y_index))
                    break
                else:
                    break
        # Left
        if self.x_position != 0:
            x_index = self.x_position - 1
            while x_index != -1:
                if board[self.y_position][x_index] is None:
                    moves_available.append((x_index, self.y_position))
                    x_index -= 1
                elif self.color != board[self.y_position][x_index].color:
                    moves_available.append((x_index, self.y_position))
                    break
                else:
                    break
        # Right
        if self.x_position != self.game.x_length - 1:
            x_index = self.x_position + 1
            while x_index != self.game.x_length:
                if board[self.y_position][x_index] is None:
                    moves_available.append((x_index, self.y_position))
                    x_index += 1
                elif self.color != board[self.y_position][x_index].color:
                    moves_available.append((x_index, self.y_position))
                    break
                else:
                    break
        if check_king:
            return self.check_check(moves_available, board, figures_dict)
        return moves_available


class Knight(Figure):
    type = 'knight'
    sign = 'k'
    value_table_white = [
        [-5,-4,-3,-3,-3,-3,-4,-5],
        [-4,-2,0,0,0,0,-2,-4],
        [-3,0,1,1.5,1.5,1,0,-3],
        [-3,0.5,1.5,2,2,1.5,0.5,-3],
        [-3,0,1.5,2,2,1.5,0,-3],
        [-3,0.5,1,1.5,1.5,1,0.5,-3],
        [-4,-2,0,0.5,0.5,0,-2,-4],
        [-5, -4, -3, -3, -3, -3, -4, -5]
    ]
    # value_table_black = value_table_white[-1::-1]
    value_table_black = list(reversed(value_table_white))

    def calculate_moves_available(self, board, figures_dict, check_king=True):
        moves_available = []
        if self.validity_test(self.x_position + 1, self.y_position - 2, board):
            moves_available.append((self.x_position + 1, self.y_position - 2))

        if self.validity_test(self.x_position + 1, self.y_position + 2, board):
            moves_available.append((self.x_position + 1, self.y_position + 2))

        if self.validity_test(self.x_position + 2, self.y_position + 1, board):
            moves_available.append((self.x_position + 2, self.y_position + 1))

        if self.validity_test(self.x_position + 2, self.y_position - 1, board):
            moves_available.append((self.x_position + 2, self.y_position - 1))

        if self.validity_test(self.x_position - 1, self.y_position - 2, board):
            moves_available.append((self.x_position - 1, self.y_position - 2))

        if self.validity_test(self.x_position - 1, self.y_position + 2, board):
            moves_available.append((self.x_position - 1, self.y_position + 2))

        if self.validity_test(self.x_position - 2, self.y_position - 1, board):
            moves_available.append((self.x_position - 2, self.y_position - 1))

        if self.validity_test(self.x_position - 2, self.y_position + 1, board):
            moves_available.append((self.x_position - 2, self.y_position + 1))
        if check_king:
            return self.check_check(moves_available, board, figures_dict)
        return moves_available


class Bishop(Figure):
    type = 'bishop'
    sign = 'B'
    value_table_white = [
        [-2,-1,-1,-1,-1,-1,-1,-2],
        [-1,0,0,0,0,0,0,-1],
        [-1,0,0,0,0,0,0,-1],
        [-1,0.5,0.5,1,1,0.5,0.5,-1],
        [-1,0,1,1,1,1,0,-1],
        [-1,1,1,1,1,1,1,-1],
        [-1,0.5,0,0,0,0,0.5,-1],
        [-2,-1,-1,-1,-1,-1,-1,-2]
    ]
    # value_table_black = value_table_white[-1::-1]
    value_table_black = list(reversed(value_table_white))

    def calculate_moves_available(self, board, figures_dict, check_king=True):
        moves_available = []
        x_index = self.x_position + 1
        y_index = self.y_position + 1
        while self.validity_test(x_index, y_index, board):
            moves_available.append((x_index, y_index))
            if board[y_index][x_index] is None:
                x_index += 1
                y_index += 1
            else:
                break
        x_index = self.x_position + 1
        y_index = self.y_position - 1
        while self.validity_test(x_index, y_index, board):
            moves_available.append((x_index, y_index))
            if board[y_index][x_index] is None:
                x_index += 1
                y_index -= 1
            else:
                break
        x_index = self.x_position - 1
        y_index = self.y_position - 1
        while self.validity_test(x_index, y_index, board):
            moves_available.append((x_index, y_index))
            if board[y_index][x_index] is None:
                x_index -= 1
                y_index -= 1
            else:
                break
        x_index = self.x_position - 1
        y_index = self.y_position + 1
        while self.validity_test(x_index, y_index, board):
            moves_available.append((x_index, y_index))
            if board[y_index][x_index] is None:
                x_index -= 1
                y_index += 1
            else:
                break
        if check_king:
            return self.check_check(moves_available, board, figures_dict)
        return moves_available


class Queen(Bishop, Rook):

    type = 'queen'
    sign = 'Q'
    value_table_white = [
        [-2, -1, -1, -0.5, -0.5, -1, -1, -2],
        [-1, 0, 0, 0, 0, 0, 0, 0, -1],
        [-1, 0, 0.5, 0.5, 0.5, 0.5, 0, -1],
        [-0.5, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
        [0, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
        [-1, 0.5, 0.5, 0.5, 0.5, 0.5, 0, -1],
        [-1, 0, 0.5, 0, 0, 0, 0, -1],
        [-2, -1, -1, -0.5, -0.5, -1, -1, -2]
    ]
    # value_table_black = value_table_white[-1::-1]
    value_table_black = list(reversed(value_table_white))

    def calculate_moves_available(self, board, figures_dict, check_king=True):
        moves_available = []
        x_index = self.x_position + 1
        y_index = self.y_position + 1
        while self.validity_test(x_index, y_index, board):
            moves_available.append((x_index, y_index))
            if board[y_index][x_index] is None:
                x_index += 1
                y_index += 1
            else:
                break
        x_index = self.x_position + 1
        y_index = self.y_position - 1
        while self.validity_test(x_index, y_index, board):
            moves_available.append((x_index, y_index))
            if board[y_index][x_index] is None:
                x_index += 1
                y_index -= 1
            else:
                break
        x_index = self.x_position - 1
        y_index = self.y_position - 1
        while self.validity_test(x_index, y_index, board):
            moves_available.append((x_index, y_index))
            if board[y_index][x_index] is None:
                x_index -= 1
                y_index -= 1
            else:
                break
        x_index = self.x_position - 1
        y_index = self.y_position + 1
        while self.validity_test(x_index, y_index, board):
            moves_available.append((x_index, y_index))
            if board[y_index][x_index] is None:
                x_index -= 1
                y_index += 1
            else:
                break

        # Downwards
        if self.y_position != self.game.y_length - 1:
            y_index = self.y_position + 1
            while y_index != self.game.y_length:
                if board[y_index][self.x_position] is None:
                    moves_available.append((self.x_position, y_index))
                    y_index += 1
                elif self.color != board[y_index][self.x_position].color:
                    moves_available.append((self.x_position, y_index))
                    break
                else:
                    break
        # Upwards
        if self.y_position != 0:
            y_index = self.y_position - 1
            while y_index != -1:
                if board[y_index][self.x_position] is None:
                    moves_available.append((self.x_position, y_index))
                    y_index -= 1
                elif self.color != board[y_index][self.x_position].color:
                    moves_available.append((self.x_position, y_index))
                    break
                else:
                    break
        # Left
        if self.x_position != 0:
            x_index = self.x_position - 1
            while x_index != -1:
                if board[self.y_position][x_index] is None:
                    moves_available.append((x_index, self.y_position))
                    x_index -= 1
                elif self.color != board[self.y_position][x_index].color:
                    moves_available.append((x_index, self.y_position))
                    break
                else:
                    break
        # Right
        if self.x_position != self.game.x_length - 1:
            x_index = self.x_position + 1
            while x_index != self.game.x_length:
                if board[self.y_position][x_index] is None:
                    moves_available.append((x_index, self.y_position))
                    x_index += 1
                elif self.color != board[self.y_position][x_index].color:
                    moves_available.append((x_index, self.y_position))
                    break
                else:
                    break

        if check_king:
            return self.check_check(moves_available, board, figures_dict)
        return moves_available


class King(Figure):

    type = 'king'
    sign = 'K'
    value_table_white = [
        [-3, -4, -4, -5, -5, -4, -4, -3],
        [-3, -4, -4, -5, -5, -4, -4, -3],
        [-3, -4, -4, -5, -5, -4, -4, -3],
        [-3, -4, -4, -5, -5, -4, -4, -3],
        [-2, -3, -3, -4, -4, -3, -3, -2],
        [-1, -2, -2, -2, -2, -2, -2, -1],
        [2, 2, 0, 0, 0, 0, 2, 2],
        [2, 3, 1, 0, 0, 1, 3, 2]
    ]
    # value_table_black = value_table_white[-1::-1]
    value_table_black = list(reversed(value_table_white))

    def calculate_moves_available(self, board, figures_dict, check_king=True):
        moves_available = []
        x_index = self.x_position + 0
        y_index = self.y_position + 1
        if self.validity_test(x_index, y_index, board):
            moves_available.append((x_index, y_index))

        x_index = self.x_position + 0
        y_index = self.y_position - 1
        if self.validity_test(x_index, y_index, board):
            moves_available.append((x_index, y_index))

        x_index = self.x_position + 1
        y_index = self.y_position + 0
        if self.validity_test(x_index, y_index, board):
            moves_available.append((x_index, y_index))

        x_index = self.x_position - 1
        y_index = self.y_position + 0
        if self.validity_test(x_index, y_index, board):
            moves_available.append((x_index, y_index))

        x_index = self.x_position + 1
        y_index = self.y_position + 1
        if self.validity_test(x_index, y_index, board):
            moves_available.append((x_index, y_index))

        x_index = self.x_position + 1
        y_index = self.y_position - 1
        if self.validity_test(x_index, y_index, board):
            moves_available.append((x_index, y_index))

        x_index = self.x_position - 1
        y_index = self.y_position + 1
        if self.validity_test(x_index, y_index, board):
            moves_available.append((x_index, y_index))

        x_index = self.x_position - 1
        y_index = self.y_position - 1
        if self.validity_test(x_index, y_index, board):
            moves_available.append((x_index, y_index))

        # Castling

            if self.color == Color.White.value:
                if self.x_position == 4 and self.y_position == 7 \
                        and not self.moved \
                        and not self.game.player_dict['white'].is_king_attacked():
                    # Left
                    if board[7][0] is not None and \
                                board[7][0].type == 'rook' \
                            and board[7][1] is None \
                            and board[7][2] is None \
                            and board[7][3] is None \
                            and not self.game.is_cell_attacked(self.game.current_player, 2, 7):
                        moves_available.append((2, 7))
                    # Right
                    if board[7][7] is not None and \
                            board[7][7].type == 'rook' \
                            and board[7][6] is None \
                            and board[7][5] is None \
                            and not self.game.is_cell_attacked(self.game.current_player, 6, 7):
                        moves_available.append((6, 7))
            else:
                if self.x_position == 4 and self.y_position == 0 \
                        and not self.moved \
                        and not self.game.player_dict['black'].is_king_attacked():
                    # Left
                    if board[0][0] is not None and \
                            board[0][0].type == 'rook' \
                            and board[0][1] is None \
                            and board[0][2] is None \
                            and board[0][3] is None \
                            and not self.game.is_cell_attacked(self.game.current_player, 2, 0):
                        moves_available.append((2, 0))
                    # Right
                    if board[0][7] is not None and \
                            board[0][7].type == 'rook' \
                            and board[0][6] is None \
                            and board[0][5] is None \
                            and not self.game.is_cell_attacked(self.game.current_player, 6, 0):
                        moves_available.append((6, 0))
        if check_king:
            return self.check_check(moves_available, board, figures_dict)
        return moves_available
