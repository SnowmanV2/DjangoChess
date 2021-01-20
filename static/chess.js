const numbers_to_literals = {
    "1": "a",
    "2": "b",
    "3": "c",
    "4": "d",
    "5": "e",
    "6": "f",
    "7": "g",
    "8": "h"
    };
const literals_to_numbers = {
    "a": 1,
    "b": 2,
    "c": 3,
    "d": 4,
    "e": 5,
    "f": 6,
    "g": 7,
    "h": 8
}
const static_figure_root = "/static/images/chessFigures/wikipedia/"
const figure_to_link = {
    "black_rook": static_figure_root + "bR.png",
    "black_knight": static_figure_root + "bN.png",
    "black_bishop": static_figure_root + "bB.png",
    "black_queen": static_figure_root + "bQ.png",
    "black_king": static_figure_root + "bK.png",
    "black_pawn": static_figure_root + "bP.png",
    "white_rook": static_figure_root + "wR.png",
    "white_knight": static_figure_root + "wN.png",
    "white_bishop": static_figure_root + "wB.png",
    "white_queen": static_figure_root + "wQ.png",
    "white_king": static_figure_root + "wK.png",
    "white_pawn": static_figure_root + "wP.png"
}
let current_player = null;
let selected_figure = null;
let is_in_progress = false;
let is_first_time = true;
let chess_json = null;
let chess_players = null;
let chess_field = null;
let move_first = null;
let move_second = null;
const items = document.getElementsByClassName("chessCell");
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');
async function send(url, data) {
    let send_to_server = await fetch(url, {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json;charset=utf-8'
    },
    body: data
});
    console.log(send_to_server);
    return await send_to_server.json()
}
function show_board() {
    chess_field.forEach(function (item, index_y) {
        item.forEach(function (item, index_x) {
            if (item === null) {
                items.namedItem(position_to_id(index_x, index_y)).textContent = "";
                items.namedItem(position_to_id(index_x, index_y)).style.backgroundImage = null;
            }
            else {
                let id = position_to_id(item["x_position"], item["y_position"]);
                items.namedItem(id).textContent = "";
                // items.namedItem(id).style.backgroundImage = "url(/static/images/chessFigures/wikipedia/bB.png)";
                items.namedItem(id).style.backgroundImage = 'url(' + figure_to_link[item["color"] + '_' + item["type"]] + ')';
            }
        })
    })
}
function highlight_moves(figure) {
    figure["moves_available"].forEach(function(item) {
        let position_y = item[1];
        let position_x = item[0];
        let id = position_to_id(position_x, position_y);
        // items.namedItem(id).textContent = 'You can move here! ^^';
        items.namedItem(id).style.backgroundColor = '#85d6a0';
    })
}
function dehighlight_moves(figure) {
    figure["moves_available"].forEach(function(item) {
        let position_y = item[1];
        let position_x = item[0];
        let id = position_to_id(position_x, position_y);
        // items.namedItem(id).textContent = '';
        items.namedItem(id).style.backgroundColor = null;
    })
}
function id_to_position(id) {
    return {"position_x": literals_to_numbers[id[0]] - 1,
            "position_y": 8 - Number(id[1])};
}
function position_to_id(x_position, y_position) {
    return numbers_to_literals[String(x_position + 1)] + String(8 - y_position);
}
function is_figure_on_cell(players, x_position, y_position) {
    for (let i = 0; i !== 2; ++i) {
        let player = players[String(i)];
        let figures_list = player["figures_list"];
        figures_list.forEach(function (item) {
            let current_position_x = item["current_position"][0] + 1;
            let current_position_y = 8 - item["current_position"][1];
            if (x_position === current_position_x && y_position === current_position_y) {
                return true;
            }
        })
    }
    return false;
}
function has_coordinates(moves_available, x_position, y_position) {
    return moves_available.some(function(item) {
        return item['0'] === x_position && item['1'] === y_position;
    })
}
function set_next_player() {
    if (current_player === 'white') {
        current_player = 'black';
    }
    else {
        current_player = 'white';
    }
}
async function chess_field_logic() {
   for (let i = 0; i !== 64; ++i) {
    await items.item(i).addEventListener("click", async function(e, the_item=items.item(i)) {
        if (move_first === null) {
            let position = id_to_position(the_item.id);
            if (chess_field[position.position_y][position.position_x] !== null
                    && current_player === chess_field[position.position_y][position.position_x]['color']) {
                selected_figure = chess_field[position.position_y][position.position_x]
                move_first = the_item.id;
                highlight_moves(selected_figure);
            }
        }
        else {
            let position = id_to_position(the_item.id);
            if (has_coordinates(selected_figure["moves_available"], position.position_x, position.position_y)) {
                dehighlight_moves(selected_figure);
                selected_figure = null;
                move_second = the_item.id;
                let command = "move " + move_first + " " + move_second;
                move_first = null;
                move_second = null;
                let json_data = JSON.stringify({"chess_turn": command});
                chess_json = await send("chessInfo", json_data);
                if (chess_json.hasOwnProperty("error")) {
                    return -1;
                }
                chess_field = chess_json["field"];
                chess_players = chess_json["players"];
                set_next_player();
                document.getElementById("game_state").textContent = current_player + ' turn';
                show_board()
                if (chess_json["victory"] !== null) {
                    is_in_progress = false
                    document.getElementById("game_state").textContent = String(chess_json["victory"]["color"]) + " won!";
                    alert(String(chess_json["victory"]["color"]) + " won!");
                }
            }
            else {
                dehighlight_moves(selected_figure);
                selected_figure = null;
                move_first = null;
                move_second = null;
            }
        }
    });
}
}
async function init() {
   if (!is_in_progress) {
       is_in_progress = true;
       is_first_time = false;
       chess_json = await send("chessInfo", JSON.stringify({"chess_turn": null}));
       chess_field = chess_json["field"];
       chess_players = chess_json["players"];
       current_player = chess_json["current_player"];
       document.getElementById("game_state").textContent = current_player + ' turn';
       show_board();
   }
}
async function after_init() {
    await document.getElementById("restart_button").addEventListener("click", async function (e) {
        is_in_progress = false;
        let json_data = {
            "command": "restart"
        };
        let response_json = await send("chessInfo", JSON.stringify(json_data));
        if (response_json["response"] === "success") {
            await init();
        }
    })
    await chess_field_logic()
}
init()
    .then(() => after_init());
