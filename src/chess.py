from abc import ABC, abstractmethod
from src.utils import MoveNotAvailableError, Color, EmptyFieldError, States
from src.figures import Figure, Rook, Knight, Bishop, Queen, King, Pawn
import random
import copy
import time
# TODO: en passant - match history needed
# TODO: match history.
# TODO: two broken things here: a) check_check method b) alpha-beta stuff
# TODO: fix check_check - instead of turn emulate - generate only essential turns(fields nearby king and vectors)
# TODO: Another thing - go from list calculation to generators - dunno how to do it now tho
# TODO: Alpha-beta seems broken - with it computer is ridiculously more stupid. Should not.
counter = 0


class Game(ABC):
    letters_to_numbers_dict = {
        'a': 1,
        'b': 2,
        'c': 3,
        'd': 4,
        'e': 5,
        'f': 6,
        'g': 7,
        'h': 8
    }
    numbers_to_letters_dict = {
        1: 'a',
        2: 'b',
        3: 'c',
        4: 'd',
        5: 'e',
        6: 'f',
        7: 'g',
        8: 'h'
    }
    type = None

    @abstractmethod
    def generate_id(self):
        pass

    @abstractmethod
    def add_game_in_collections(self):
        pass

    @abstractmethod
    def remove_game_from_collections(self):
        pass

    @classmethod
    def get_type(cls):
        return cls.type

    def __init__(self, game_id=None):
        # Server side game features
        # Storing and distributing
        if game_id is None:
            self.id = self.generate_id()
        else:
            self.id = game_id
        self.type = self.get_type()
        self.players_amount = 1
        self.add_game_in_collections()
        self.turns = "";
        # Gameplay side game features
        # Rules and stuff
        self.victorious = None
        self.current_player = None
        self.user_input = None
        self.is_in_progress = True
        self.x_length = 8
        self.y_length = 8
        self.chess_field = [
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None]
        ]
        if isinstance(self, VersusAIGame):
            self.PLAYER_BLACK = AIPlayer(Color.Black.value, game=self)
        else:
            self.PLAYER_BLACK = Player(Color.Black.value, game=self)
        # self.PLAYER_WHITE = AIPlayer(Color.White.value, game=self)
        self.PLAYER_WHITE = Player(Color.White.value, game=self)

        self.players = [self.PLAYER_WHITE, self.PLAYER_BLACK]
        self.player_dict = {'white': self.PLAYER_WHITE, 'black': self.PLAYER_BLACK}
        figures_black_list, figures_black_dict = self.__get_black_figures()
        self.PLAYER_BLACK.figures_list = figures_black_list
        self.PLAYER_BLACK.figures_dict = figures_black_dict

        figures_white_list, figures_white_dict = self.__get_white_figures()
        self.PLAYER_WHITE.figures_list = figures_white_list
        self.PLAYER_WHITE.figures_dict = figures_white_dict
        self.update_game_state()
        self.set_next_player()

    def update_game_state(self):
        for player in self.players:
            player.update_figures_moves(check_king=False)
            if player.is_king_attacked():
                player.king_attacked = True
            else:
                player.king_attacked = False

    def set_next_player(self):
        if self.current_player is None:
            self.current_player = self.players[0]
        else:
            if self.current_player == self.player_dict['white']:
                self.current_player = self.player_dict['black']
            else:
                self.current_player = self.player_dict['white']

    def __get_black_figures(self):
        figures_black_list = []
        figures_black_dict = {'pawns': []}
        # rook
        self.chess_field[0][0] = Rook(0, 0, Color.Black.value, self)
        figures_black_list.append(self.chess_field[0][0])
        figures_black_dict['rook_left'] = self.chess_field[0][0]
        # knight
        self.chess_field[0][1] = Knight(1, 0, Color.Black.value, self)
        figures_black_list.append(self.chess_field[0][1])
        figures_black_dict['knight_left'] = self.chess_field[0][1]
        # bishop
        self.chess_field[0][2] = Bishop(2, 0, Color.Black.value, self)
        figures_black_list.append(self.chess_field[0][2])
        figures_black_dict['bishop_left'] = self.chess_field[0][2]
        # Queen
        self.chess_field[0][3] = Queen(3, 0, Color.Black.value, self)
        figures_black_list.append(self.chess_field[0][3])
        figures_black_dict['queen'] = self.chess_field[0][3]
        # King
        self.chess_field[0][4] = King(4, 0, Color.Black.value, self)
        figures_black_list.append(self.chess_field[0][4])
        figures_black_dict['king'] = self.chess_field[0][4]
        # bishop
        self.chess_field[0][5] = Bishop(5, 0, Color.Black.value, self)
        figures_black_list.append(self.chess_field[0][5])
        figures_black_dict['bishop_right'] = self.chess_field[0][5]
        # knight
        self.chess_field[0][6] = Knight(6, 0, Color.Black.value, self)
        figures_black_list.append(self.chess_field[0][6])
        figures_black_dict['knight_right'] = self.chess_field[0][6]
        # rook
        self.chess_field[0][7] = Rook(7, 0, Color.Black.value, self)
        figures_black_list.append(self.chess_field[0][7])
        figures_black_dict['rook_right'] = self.chess_field[0][7]
        # pawns
        for i in range(0, 8):
            self.chess_field[1][i] = Pawn(i, 1, Color.Black.value, self)
            figures_black_list.append(self.chess_field[1][i])
            figures_black_dict['pawns'].append(self.chess_field[1][i])
        return figures_black_list, figures_black_dict

    def __get_white_figures(self):
        figures_white_list = []
        figures_white_dict = {'pawns': []}
        # rook
        self.chess_field[7][0] = Rook(0, 7, Color.White.value, self)
        figures_white_list.append(self.chess_field[7][0])
        figures_white_dict['rook_left'] = self.chess_field[7][0]
        # knight
        self.chess_field[7][1] = Knight(1, 7, Color.White.value, self)
        figures_white_list.append(self.chess_field[7][1])
        figures_white_dict['knight_left'] = self.chess_field[7][1]
        # bishop
        self.chess_field[7][2] = Bishop(2, 7, Color.White.value, self)
        figures_white_list.append(self.chess_field[7][2])
        figures_white_dict['bishop_left'] = self.chess_field[7][2]
        # queen
        self.chess_field[7][3] = Queen(3, 7, Color.White.value, self)
        figures_white_list.append(self.chess_field[7][3])
        figures_white_dict['queen'] = self.chess_field[7][3]
        # king
        self.chess_field[7][4] = King(4, 7, Color.White.value, self)
        figures_white_list.append(self.chess_field[7][4])
        figures_white_dict['king'] = self.chess_field[7][4]
        # bishop
        self.chess_field[7][5] = Bishop(5, 7, Color.White.value, self)
        figures_white_list.append(self.chess_field[7][5])
        figures_white_dict['bishop_right'] = self.chess_field[7][5]
        # knight
        self.chess_field[7][6] = Knight(6, 7, Color.White.value, self)
        figures_white_list.append(self.chess_field[7][6])
        figures_white_dict['knight_right'] = self.chess_field[7][6]
        # rook
        self.chess_field[7][7] = Rook(7, 7, Color.White.value, self)
        figures_white_list.append(self.chess_field[7][7])
        figures_white_dict['rook_right'] = self.chess_field[7][7]
        # pawns
        for i in range(0, 8):
            self.chess_field[6][i] = Pawn(i, 6, Color.White.value, self)
            figures_white_list.append(self.chess_field[6][i])
            figures_white_dict['pawns'].append(self.chess_field[6][i])
        return figures_white_list, figures_white_dict

    def chess_field_update(self, figure, new_coordinates):
        old_x_position, old_y_position = figure.current_position
        new_x_position, new_y_position = new_coordinates
        self.chess_field[old_y_position][old_x_position] = None
        if self.chess_field[new_y_position][new_x_position] is None:
            self.chess_field[new_y_position][new_x_position] = figure
        else:
            eaten_figure = self.chess_field[new_y_position][new_x_position]
            self.chess_field[new_y_position][new_x_position] = figure
            self.player_dict[eaten_figure.color].eaten_figures.append(eaten_figure)
            self.player_dict[eaten_figure.color].figures_list.remove(eaten_figure)
            eaten_figure.is_eaten = True

    def get_chess_json(self):
        data_dict = {
            "players": self.players,
            "field": self.chess_field,
            "victory": self.victorious,
            "current_player": self.current_player.color
        }
        return data_dict

    def make_turn(self):
        user_input_splitted = self.current_player.user_input.split()
        if user_input_splitted[0] == 'move':
            start_coordinates_x, start_coordinates_y = self.__convert_coordinates(
                (
                    self.letters_to_numbers_dict[user_input_splitted[1][0]],
                    user_input_splitted[1][1]
                )
            )
            end_coordinates_x, end_coordinates_y = self.__convert_coordinates(
                (
                    self.letters_to_numbers_dict[user_input_splitted[2][0]],
                    user_input_splitted[2][1]
                )
            )
            if self.chess_field[start_coordinates_y][start_coordinates_x] is None:
                raise EmptyFieldError('There are no figure in there.')
            if self.chess_field[start_coordinates_y][start_coordinates_x].color != self.current_player.color:
                raise MoveNotAvailableError('The figure is not yours lel')
            self.chess_field[start_coordinates_y][start_coordinates_x].move(end_coordinates_x, end_coordinates_y)
            self.turns += f'{self.current_player.user_input}\n'
            if self.is_victory(self.current_player):
                self.is_in_progress = False
                self.victorious = self.current_player
                self.remove_game_from_collections()

    def __convert_coordinates(self, coordinates):
        x_position, y_position = coordinates
        return int(x_position) - 1, self.y_length - int(y_position)

    def is_victory(self, player):
        # chess
        if player == self.PLAYER_WHITE:
            enemy_player = self.PLAYER_BLACK
        else:
            enemy_player = self.PLAYER_WHITE
        for figure in enemy_player.figures_list:
            if len(figure.moves_available) != 0:
                return False
        if enemy_player.is_king_attacked():
            return True
        else:
            return False

    @staticmethod
    def is_cell_attacked(current_player, x_position, y_position):
        for figure in current_player.figures_list:
            if (x_position, y_position) in figure.moves_available:
                return True
        return False

    def to_json(self):
        return self.__dict__


class MeleeGame(Game):
    type = 'melee'
    games_dict = {}
    pending_games = {}

    def generate_id(self):
        game_id = random.randint(1, 10000)
        while MeleeGame.games_dict.get(game_id, None) is not None \
                and MeleeGame.pending_games.get(game_id) is not None:
            game_id = random.randint(1, 10000)
        return game_id

    def add_game_in_collections(self):
        if self.state == States.PENDING.value:
            MeleeGame.pending_games[str(self.id)] = self
            while MeleeGame.pending_games.get(str(self.id)) is None:
                MeleeGame.pending_games[str(self.id)] = self
        elif self.state == States.IN_PROGRESS.value:
            del MeleeGame.pending_games[str(self.id)]
            MeleeGame.games_dict[str(self.id)] = self

    def remove_game_from_collections(self):
        if self.state == States.PENDING.value:
            del MeleeGame.pending_games[str(self.id)]
        else:
            del MeleeGame.games_dict[str(self.id)]

    def __init__(self, *args, **kwargs):
        self.state = States.PENDING.value
        self.colors_dict = {
        'white': None,
        'black': None
        }
        super().__init__(*args, **kwargs)


class HotSeatGame(Game):
    type = 'hotseat'
    games_dict = {}

    def generate_id(self):
        game_id = random.randint(1, 10000)
        while HotSeatGame.games_dict.get(game_id, None) is not None:
            game_id = random.randint(1, 10000)
        return game_id

    def add_game_in_collections(self):
        HotSeatGame.games_dict[str(self.id)] = self

    def remove_game_from_collections(self):
        del HotSeatGame.games_dict[str(self.id)]


class VersusAIGame(Game):
    type = "ai"
    games_dict = {}

    def __init__(self, difficulty, game_id=None):
        self.difficulty = difficulty
        super().__init__(game_id)

    def generate_id(self):
        game_id = random.randint(1, 10000)
        while VersusAIGame.games_dict.get(game_id, None) is not None:
            game_id = random.randint(1, 10000)
        return game_id

    def add_game_in_collections(self):
        VersusAIGame.games_dict[str(self.id)] = self

    def remove_game_from_collections(self):
        del VersusAIGame.games_dict[str(self.id)]


class Player:
    type = 'human'

    def __init__(self, color, figures_list=None, figures_dict=None, name='Anonimous', game=None):
        self.user_input = None
        self.game = game
        if figures_dict is None:
            figures_dict = {}
        if figures_list is None:
            figures_list = []
        self.name = name
        self.color = color
        self.figures_list = figures_list
        self.figures_dict = figures_dict
        self.eaten_figures = []
        self.king_attacked = False

    def set_user_input(self, user_input=None):
        self.user_input = user_input

    def update_figures_moves(self, check_king=True):
        enemy_color = 'white' if self.color == 'black' else 'black'
        for figure in self.figures_list:
            if not figure.is_eaten:
                figure.moves_available = figure.calculate_moves_available(self.game.chess_field, {self.color: self.figures_list, enemy_color: self.game.player_dict[enemy_color].figures_list, self.color + '_king': self.figures_dict["king"], enemy_color + '_king': self.game.player_dict[enemy_color].figures_dict["king"]}, check_king)
            else:
                figure.moves_available = []

    def is_king_attacked(self):
        if self.color == Color.White.value:
            for figure in self.game.player_dict[Color.Black.value].figures_list:
                if self.figures_dict['king'].current_position in figure.moves_available:
                    return True
            return False
        else:
            for figure in self.game.player_dict[Color.White.value].figures_list:
                if self.figures_dict['king'].current_position in figure.moves_available:
                    return True
            return False

    def to_json(self):
        return {
            "name": self.name,
            "color": self.color,
            "figures_list": self.figures_list,
            "figures_dict": self.figures_dict,
            "eaten_figures": self.eaten_figures,
            "king_attacked": self.king_attacked
        }


class AIPlayer(Player):
    type = 'ai'
    numbers_to_letters_dict = {
        1: 'a',
        2: 'b',
        3: 'c',
        4: 'd',
        5: 'e',
        6: 'f',
        7: 'g',
        8: 'h'
    }

    def __convert_coordinates_to_computer(self, coordinates):
        x_position, y_position = coordinates
        return int(x_position) - 1, self.game.y_length - int(y_position)

    def __convert_coordinates_to_gui(self, coordinates):
        x_position, y_position = coordinates
        return int(x_position) + 1, self.game.y_length - int(y_position)

    def set_user_input(self, user_input=None):

        if self.game.difficulty == 1:
            self.user_input = self.make_decision_random()
        elif self.game.difficulty == 2:
            self.user_input = self.make_decision_minimax(self.color, 1)
        else:
            self.user_input = self.make_decision_minimax(self.color, 2)
        print(self.game.difficulty)

    def make_decision_minimax(self, ai_color, max_deepness):
        def lurk_deeper(chess_board, player_color, alpha, beta, current_deepness=0):
            global counter
            print(counter)
            counter += 1

            if current_deepness == max_deepness:
                return self.get_position_value(chess_board, ai_color)
            minMax = -999999.0 if player_color == ai_color else 999999.0
            bestMove = None

            for figure in chess_board.figures[player_color]:
                for move in figure.moves_available:
                    print(figure.type)
                    total_time = 0
                    start_time = time.time()
                    turn = self.get_turn_from_decision(figure, move)
                    chess_board.make_turn(figure, move)
                    total_time += time.time() - start_time
                    print("--- Turn: %s seconds ---" % (time.time() - start_time))
                    start_time = time.time()
                    turn_value = lurk_deeper(chess_board, 'black' if player_color == 'white' else 'white',
                                             alpha, beta, current_deepness + 1)

                    if (turn_value >= minMax and player_color == ai_color) or \
                            (turn_value <= minMax and player_color != ai_color):
                        minMax = turn_value
                        bestMove = turn
                    total_time += time.time() - start_time
                    print("--- Recursive: %s seconds ---" % (time.time() - start_time))
                    start_time = time.time()
                    chess_board.undo_turn()
                    total_time += time.time() - start_time
                    print("--- Undo: %s seconds ---" % (time.time() - start_time))
                    start_time = time.time()
                    if player_color == ai_color:
                        alpha = max(alpha, turn_value)
                    else:
                        beta = min(beta, turn_value)
                    total_time += time.time() - start_time
                    print("--- alpha-beta: %s seconds ---" % (time.time() - start_time))
                    print("--- total: %s seconds ---" % (total_time))

                    if beta < alpha:
                        return minMax


            final_decision = {"turn": bestMove, "value": minMax}

            if current_deepness == 0:
                return final_decision["turn"]
            else:
                return final_decision["value"]

        chess_board = Board(self.game.chess_field)
        # current_player = copy.deepcopy(self.game.current_player)
        start_time = time.time()
        result = lurk_deeper(chess_board, self.color, -9999999.0, 9999999.0)
        print("---total time %s seconds ---" % (time.time() - start_time))
        global counter
        counter = 0
        # print("result: ", result)
        return result

    def make_decision_random(self):
        print('im here in random')
        figure = random.choice(self.figures_list)
        while len(figure.moves_available) == 0:
            figure = random.choice(self.figures_list)
        move = random.choice(figure.moves_available)
        return self.get_turn_from_decision(figure, move)

    def get_position_value(self, chess_board, player_color):
        total_value = 0.0
        if player_color == 'white':
            enemy_player_color = 'black'
        else:
            enemy_player_color = 'white'
        for figure in chess_board.figures[player_color]:
            total_value += self.get_value_of_object(figure)
        for figure in chess_board.figures[enemy_player_color]:
            total_value -= self.get_value_of_object(figure)
        return total_value

    def get_value_of_object(self, obj):
        position_x, position_y = obj.current_position
        if obj.color == 'white':
            value = float(obj.value_table_white[position_y][position_x])
        else:
            value = float(obj.value_table_black[position_y][position_x])

        if isinstance(obj, Pawn):
            value += 10
        elif isinstance(obj, Queen):
            value += 30
        elif isinstance(obj, Bishop):
            value += 30
        elif isinstance(obj, Rook):
            value += 50
        elif isinstance(obj, Knight):
            value += 90
        elif isinstance(obj, King):
            value += 10000
        return value

    def get_turn_from_decision(self, figure, move):
        initial_x, initial_y = self.__convert_coordinates_to_gui(figure.current_position)
        dest_x, dest_y = self.__convert_coordinates_to_gui(move)
        decision = \
            f'move {self.numbers_to_letters_dict[initial_x]}{initial_y} {self.numbers_to_letters_dict[dest_x]}{dest_y}'
        return decision


class Board:
    letters_to_numbers_dict = {
        'a': 1,
        'b': 2,
        'c': 3,
        'd': 4,
        'e': 5,
        'f': 6,
        'g': 7,
        'h': 8
    }

    @staticmethod
    def __convert_coordinates_to_computer(coordinates):
        x_position, y_position = coordinates
        return int(x_position) - 1, 8 - int(y_position)

    def get_turn_from_input(self, input):
        items = input.split(' ')
        initial_coordinates = (self.letters_to_numbers_dict[items[1][0]], items[1][1])
        destination_coordinates = (self.letters_to_numbers_dict[items[2][0]], items[2][1])
        initial_x, initial_y = self.__convert_coordinates_to_computer(initial_coordinates)
        dest_x, dest_y = self.__convert_coordinates_to_computer(destination_coordinates)
        return self.current_board[initial_y][initial_x], (dest_x, dest_y)

    def __init__(self, board=None):
        self.x_length = 8
        self.y_length = 8
        if board is None:
            self.current_board = [
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None]
            ]
            self.__init_board()
        else:
            self.current_board = copy.deepcopy(board)
        self.previous_turns = []
        self.figures = {
            "white": [],
            "black": []
        }
        for row in self.current_board:
            for cell in row:
                if cell is not None:
                    self.figures[cell.color].append(cell)
                    if isinstance(cell, King):
                        self.figures[cell.color + "_king"] = cell
        self.eaten_figures = []

    def __init_board(self):
        self.__get_black_figures()
        self.__get_white_figures()

    def __get_black_figures(self):
        # rook
        self.current_board[0][0] = Rook(0, 0, Color.Black.value, self)
        # knight
        self.current_board[0][1] = Knight(1, 0, Color.Black.value, self)
        # bishop
        self.current_board[0][2] = Bishop(2, 0, Color.Black.value, self)
        # Queen
        self.current_board[0][3] = Queen(3, 0, Color.Black.value, self)
        # King
        self.current_board[0][4] = King(4, 0, Color.Black.value, self)
        # bishop
        self.current_board[0][5] = Bishop(5, 0, Color.Black.value, self)
        # knight
        self.current_board[0][6] = Knight(6, 0, Color.Black.value, self)
        # rook
        self.current_board[0][7] = Rook(7, 0, Color.Black.value, self)
        # pawns
        for i in range(0, 8):
            self.current_board[1][i] = Pawn(i, 1, Color.Black.value, self)

    def __get_white_figures(self):
        # rook
        self.current_board[7][0] = Rook(0, 7, Color.White.value, self)
        # knight
        self.current_board[7][1] = Knight(1, 7, Color.White.value, self)
        # bishop
        self.current_board[7][2] = Bishop(2, 7, Color.White.value, self)
        # queen
        self.current_board[7][3] = Queen(3, 7, Color.White.value, self)
        # king
        self.current_board[7][4] = King(4, 7, Color.White.value, self)
        # bishop
        self.current_board[7][5] = Bishop(5, 7, Color.White.value, self)
        # knight
        self.current_board[7][6] = Knight(6, 7, Color.White.value, self)
        # rook
        self.current_board[7][7] = Rook(7, 7, Color.White.value, self)
        # pawns
        for i in range(0, 8):
            self.current_board[6][i] = Pawn(i, 6, Color.White.value, self)

    def make_turn(self, figure, move, calculate_turns=True):
        self.previous_turns.append((figure, figure.current_position, move))
        figure_x, figure_y = figure.current_position
        dest_x, dest_y = move
        eaten_figure = self.current_board[dest_y][dest_x]
        self.current_board[dest_y][dest_x] = figure
        self.current_board[figure_y][figure_x] = None
        figure.current_position = (dest_x, dest_y)
        figure.x_position = dest_x
        figure.y_position = dest_y
        self.eaten_figures.append(eaten_figure)
        if eaten_figure is not None:
            eaten_figure.is_eaten = True
            self.figures[eaten_figure.color].remove(eaten_figure)
        if calculate_turns:
            for item in self.figures["black"]:
                item.moves_available = item.calculate_moves_available(self.current_board, self.figures, check_king=True)
                # random.shuffle(item.moves_available)
            for item in self.figures["white"]:
                item.moves_available = item.calculate_moves_available(self.current_board, self.figures, check_king=True)
                # random.shuffle(item.moves_available)

    def undo_turn(self, calculate_turns=True):
        # self.current_board = self.previous_boards.pop()
        previous_figure, previous_position, previous_move = self.previous_turns.pop()
        # self.previous_boards.pop()
        previous_figure.current_position = previous_position
        previous_x, previous_y = previous_position
        current_x, current_y = previous_move
        self.current_board[previous_y][previous_x] = previous_figure
        eaten_figure = self.eaten_figures.pop()
        self.current_board[current_y][current_x] = eaten_figure
        if previous_figure is not None:
            previous_figure.current_position = (previous_x, previous_y)
            previous_figure.x_position = previous_x
            previous_figure.y_position = previous_y
        if eaten_figure is not None:
            eaten_figure.is_eaten = False
            self.figures[eaten_figure.color].append(eaten_figure)
        if calculate_turns:
            for item in self.figures["black"]:
                item.moves_available = item.calculate_moves_available(self.current_board, self.figures, check_king=True)
                # random.shuffle(item.moves_available)
            for item in self.figures["white"]:
                item.moves_available = item.calculate_moves_available(self.current_board, self.figures, check_king=True)
                # random.shuffle(item.moves_available)

    def to_json(self):
        return self.__dict__



