import pdb
from asyncio import sleep
# from time import sleep
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import CreateView
from django.contrib.auth.models import User

from chess.models import SavedGame
from src.chess import Game, HotSeatGame, VersusAIGame, AIPlayer
from django.views import View
from django.http import HttpResponse, Http404
import json, random
from src.utils import States
import src.chess as chess
from src.utils import EmptyFieldError, MoveNotAvailableError


class ProfileView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Http404()
        games = SavedGame.objects.filter(user_id=request.user.id)
        hotseat_games = games.filter(mode="hotseat")
        melee_games = games.filter(mode="melee")
        ai_games = games.filter(mode="ai")
        context = {
            'username': request.user.username,
            'games': games,
            'hotseat_games': hotseat_games,
            'melee_games': melee_games,
            'ai_games': ai_games
        }
        return render(request, 'chess/profile.html', context=context)


class GameReplayView(View):
    replayInfoDict = {

    }
    def __init__(self, *args, **kwargs):
        self.turns = None
        self.board = None
        self.current_turn = None
        super().__init__(*args, *kwargs)

    def get(self, request, game_id, *args, **kwargs):
        context = {

        }
        return render(request, 'chess/gameReplay.html', context=context)

    def post(self, request, game_id, *args, **kwargs):
        chess_turn_json = request.body
        chess_turn_dict = json.loads(chess_turn_json)

        if chess_turn_dict.get("command", None) is not None:
            chess_command = chess_turn_dict.get("command")
            if chess_command == "init":
                turns = SavedGame.objects.get(id=game_id).turns_history.split("\n")
                board = chess.Board()
                current_turn = 0
                GameReplayView.replayInfoDict[game_id] = {
                    "turns": turns,
                    "board": board,
                    "current_turn": current_turn
                }
                json_response = {"response": "success",
                                 "field": GameReplayView.replayInfoDict[game_id]["board"].current_board,
                                 "victory": "null"}
                # print(current_turn)
                json_data = json.dumps(json_response, default=lambda obj: obj.to_json())
                return HttpResponse(json_data, content_type='application/json')
            else:
                game_info = GameReplayView.replayInfoDict[game_id]
                # print(self.current_turn)
                if chess_command == "next":
                    if game_info["current_turn"] >= len(game_info["turns"]) - 1:
                        json_response = {"response": "reject",
                                         "victory": "black" if (game_info["current_turn"]) % 2 == 0 else "white"}
                        print("hi!")
                        print(json_response["victory"])
                        return HttpResponse(json.dumps(json_response), content_type='application/json')
                    turn = game_info["turns"][game_info["current_turn"]]
                    game_info["current_turn"] += 1
                    print(game_info["current_turn"])
                    print(len(game_info["turns"]))
                    figure, move = game_info["board"].get_turn_from_input(turn)
                    game_info["board"].make_turn(figure, move, calculate_turns=False)
                    json_response = {
                        "response": "success",
                        "field": game_info["board"].current_board
                    }

                    json_data = json.dumps(json_response, default=lambda obj: obj.to_json())
                    return HttpResponse(json_data, content_type='application/json')
                else:  # chess_command == "previous"
                    if game_info["current_turn"] <= 0:
                        json_response = {
                            "response": "reject"
                        }
                        return HttpResponse(json.dumps(json_response), content_type='application/json')
                    game_info["board"].undo_turn(calculate_turns=False)
                    game_info["current_turn"] -= 1
                    json_response = {
                        "response": "success",
                        "field": game_info["board"].current_board
                    }

                    json_data = json.dumps(json_response, default=lambda obj: obj.to_json())
                    return HttpResponse(json_data, content_type='application/json')


class HotSeatChessView(View):
    # @ensure_csrf_cookie
    def get(self, request, *args, **kwargs):
        # context = RequestContext(request)
        return render(request, 'chess/chessHotSeat.html')


class AIChessView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'chess/chessAIWhite.html')


class MeleeChessView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'chess/chessMeleeWhite.html')


class MeleeWaitRoomView(View):
    def get(self, request, game_id, *args, **kwargs):
        return render(request, 'chess/waiting_game.html')

    def post(self, request, game_id, *args, **kwargs):
        request_json = request.body
        request_dict = json.loads(request_json)

        while True:
            try:
                game = chess.MeleeGame.pending_games.get(str(game_id), None)
                break
            except KeyError:
                continue
        while True:
            if request_dict["request"] == "start":
                if game is None:
                    print('game is none')
                    response = json.dumps(
                        {"start": "success", "href": request.build_absolute_uri().replace('waitRoom', '')})
                    return HttpResponse(response, content_type='application/json')
                if game.players_amount >= 2:
                    game.state = States.IN_PROGRESS.value
                    game.add_game_in_collections()
                    response = json.dumps(
                        {"start": "success", "href": request.build_absolute_uri().replace('waitRoom', '')})
                    return HttpResponse(response, content_type='application/json')
                sleep(1000)


class HotSeatStartGameView(View):
    def get(self, request):
        game = HotSeatGame()
        return redirect(f'/games/hotSeat/{game.id}/')


class MeleeStartGameView(View):
    def get(self, request):
        for i in range(0, 20):
            pending_games = chess.MeleeGame.pending_games
        for i in range(0, 20):
            len_pending_games = len(pending_games)
        if len_pending_games == 0:
            game = chess.MeleeGame()
        else:
            game = list(pending_games.values())[0]
            game.players_amount += 1
        return redirect(f'/games/melee/{game.id}/waitRoom')


class VersusAIStartGameView(View):
    def get(self, request, difficulty):
        game = VersusAIGame(int(difficulty))
        return redirect(f'/games/ai/{game.id}/')


class MainPageView(View):
    def get(self, request):
        # SavedGame.objects.all().delete()
        form = AuthenticationForm()
        context = {
            "current_user_name": "None" if not request.user.is_authenticated else request.user.username,
            "form": form
        }
        return render(request, 'chess/index.html', context=context)


class ChessInfoView(View):

    def post(self, request, game_id, *args, **kwargs):

        chess_turn_json = request.body
        chess_turn_dict = json.loads(chess_turn_json)

        if chess_turn_dict.get("command", None) is not None:
            HotSeatGame(game_id=game_id)
            return HttpResponse(json.dumps({"response": "success"}), content_type='application/json')
        while True:
            try:
                game = HotSeatGame.games_dict[str(game_id)]
                break
            except KeyError:
                continue
        if chess_turn_dict["chess_turn"] is None:
            return HttpResponse(json.dumps(game.get_chess_json(), default=lambda obj: obj.to_json()),
                                content_type='application/json')

        chess_turn = chess_turn_dict["chess_turn"]
        game.current_player.set_user_input(chess_turn)

        try:
            game.make_turn()
        except MoveNotAvailableError:
            response = json.dumps({"error": "move is not available"})
            return HttpResponse(response, content_type='application/json')
        except EmptyFieldError:
            response = json.dumps({"error": "the field is empty"})
            return HttpResponse(response, content_type='application/json')

        if not game.is_in_progress:
            if request.user.is_authenticated:
                game_state = 'tie' if game.victorious is None else \
                    'victory' if game.victorious == game.current_player else \
                    'defeat'
                SavedGame.objects.create(player_color=game.current_player, turns_history=game.turns,
                                         user_id=request.user.id,
                                         enemy_user=None, result=game_state, mode="hotseat")

        json_data = json.dumps(game.get_chess_json(), default=lambda obj: obj.to_json())
        game.set_next_player()

        return HttpResponse(json_data, content_type='application/json')


class MeleeChessInfoView(View):

    def __init__(self):
        self.user = {'white': None, 'black': None}
        super().__init__()

    def post(self, request, game_id, *args, **kwargs):
        print('Post request accepted')
        chess_turn_json = request.body
        chess_turn_dict = json.loads(chess_turn_json)
        print('Post request accepted')
        if chess_turn_dict.get("command", None) is not None:
            game = chess.MeleeGame(game_id=game_id)
            game.state = States.IN_PROGRESS.value
            game.add_game_in_collections()
            return HttpResponse(json.dumps({"response": "success"}), content_type='application/json')

        while True:
            try:
                game = chess.MeleeGame.games_dict[str(game_id)]
                break
            except KeyError:
                continue

        if chess_turn_dict.get("request", None) is not None:
            if chess_turn_dict["request"] == 'user_color':
                if game.colors_dict['white'] is None:
                    game.colors_dict['white'] = True
                    answer = "white"
                    if request.user.is_authenticated:
                        self.user['white'] = request.user
                    print("sending white color")
                elif game.colors_dict['black'] is None:
                    game.colors_dict['black'] = True
                    answer = 'black'
                    if request.user.is_authenticated:
                        self.user['black'] = request.user
                    print("sending black color")
                else:
                    answer = 'reject'
                    print("sending reject")
                return HttpResponse(json.dumps({"request": answer}), content_type='application/json')
            elif chess_turn_dict["request"] == 'update_board':
                while True:
                    user_color = chess_turn_dict["user_color"]
                    if user_color == game.current_player.color:
                        answer = game.get_chess_json()
                        answer["request"] = "success"
                        return HttpResponse(json.dumps(answer, default=lambda obj: obj.to_json()),
                                            content_type='application/json')
                    sleep(1000)

        if chess_turn_dict["chess_turn"] is None:
            return HttpResponse(json.dumps(game.get_chess_json(), default=lambda obj: obj.to_json()),
                                content_type='application/json')

        chess_turn = chess_turn_dict["chess_turn"]
        game.current_player.set_user_input(chess_turn)

        try:
            game.make_turn()
        except MoveNotAvailableError:
            response = json.dumps({"error": "move is not available"})
            return HttpResponse(response, content_type='application/json')
        except EmptyFieldError:
            response = json.dumps({"error": "the field is empty"})
            return HttpResponse(response, content_type='application/json')

        if not game.is_in_progress:
            if self.user['white'] is not None and self.user['black'] is not None:
                game_state = 'tie' if game.victorious is None else \
                    'victory' if game.victorious == game.current_player else \
                    'defeat'
                enemy_color = 'white' if game.current_player.color == 'black' else 'white'
                SavedGame.objects.create(player_color=game.current_player, turns_history=game.turns,
                                         user_id=request.user.id,
                                         enemy_user_id=self.user[enemy_color].id,
                                         result=game_state, mode="melee")
                enemy_game_state = 'tie' if game.victorious is None else \
                    'defeat' if game_state == 'victory' else \
                    'victory'
                SavedGame.objects.create(player_color=game.current_player, turns_history=game.turns,
                                         user=User.objects.get(self.user[enemy_color].id),
                                         enemy_user=User.objects.get(request.user.id),
                                         result=enemy_game_state, mode="melee")
        json_data = json.dumps(game.get_chess_json(), default=lambda obj: obj.to_json())
        game.set_next_player()

        return HttpResponse(json_data, content_type='application/json')


class AIChessInfoView(View):

    def post(self, request, game_id, *args, **kwargs):
        # Getting post info
        chess_turn_json = request.body
        chess_turn_dict = json.loads(chess_turn_json)
        # Whether game started
        if chess_turn_dict.get("command", None) is not None:
            VersusAIGame(game_id=game_id)
            return HttpResponse(json.dumps({"response": "success"}), content_type='application/json')
        # Making turn
        while True:
            try:
                game = VersusAIGame.games_dict[str(game_id)]
                break
            except KeyError:
                continue
        # If game started
        if chess_turn_dict["chess_turn"] is None:
            if isinstance(game.current_player, AIPlayer):
                game.current_player.set_user_input()
                game.make_turn()
                game.set_next_player()
            return HttpResponse(json.dumps(game.get_chess_json(), default=lambda obj: obj.to_json()),
                                content_type='application/json')
        # If game in progress
        # Human turn
        if isinstance(game.current_player, AIPlayer):
            game.current_player.set_user_input()
        else:
            chess_turn = chess_turn_dict["chess_turn"]
            game.current_player.set_user_input(chess_turn)

        try:
            game.make_turn()
        except MoveNotAvailableError:
            response = json.dumps({"error": "move is not available"})
            return HttpResponse(response, content_type='application/json')
        except EmptyFieldError:
            response = json.dumps({"error": "the field is empty"})
            return HttpResponse(response, content_type='application/json')

        if not game.is_in_progress:
            if request.user.is_authenticated:
                game_state = 'tie' if game.victorious is None else \
                    'victory' if game.victorious == game.current_player else \
                    'defeat'
                SavedGame.objects.create(player_color=game.current_player, turns_history=game.turns,
                                         user_id=request.user.id, enemy_user=None,
                                         result=game_state, mode="ai")
                print(SavedGame.objects.first().user.id)
        json_data = json.dumps(game.get_chess_json(), default=lambda obj: obj.to_json())
        game.set_next_player()
        return HttpResponse(json_data, content_type='application/json')


class HyperSignUpView(CreateView):
    form_class = UserCreationForm
    success_url = '/login'
    template_name = 'chess/signup.html'


class HyperLoginView(LoginView):
    form_class = AuthenticationForm
    redirect_authenticated_user = True
    template_name = 'chess/login.html'
