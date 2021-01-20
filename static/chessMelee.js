import {
    numbers_to_literals, literals_to_numbers, static_figure_root, figure_to_link,
    show_board, highlight_moves, dehighlight_moves, id_to_position, position_to_id,
    is_figure_on_cell, has_coordinates, set_next_player, items
} from "/static/chessGeneral.js";
let user_color = null;
let current_player = null;
let selected_figure = null;
let is_in_progress = false;
let is_first_time = true;
let chess_json = null;
let chess_players = null;
let chess_field = null;
let move_first = null;
let move_second = null;

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
    console.log("sending color request");
    console.log(url);
    console.log(data);
    console.log(csrftoken);
    // url = "123"
    let send_to_server = await fetch(url, {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json;charset=utf-8'
    },
    body: data
});
    console.log(send_to_server)
    return await send_to_server.json()
}
async function get_user_color() {
    let response_json = await send("chessInfo", JSON.stringify({"request": "user_color"}));
    console.log("got response");
    while (response_json["request"] === "reject") {
        response_json = await send("chessInfo", JSON.stringify({"request": "user_color"}));
    }
    if (response_json["request"] !== "reject") {
        user_color = response_json["request"];
        if (user_color === 'black') {
            run_chess_updater();
        }
        console.log(user_color);
    }
}

async function chess_field_logic() {
    for (let i = 0; i !== 64; ++i) {
        await items.item(i).addEventListener("click", async function (e, the_item = items.item(i)) {

            if (move_first === null) {
                let position = id_to_position(the_item.id);
                if (chess_field[position.position_y][position.position_x] !== null
                    && user_color === chess_field[position.position_y][position.position_x]['color']) {
                    selected_figure = chess_field[position.position_y][position.position_x]
                    move_first = the_item.id;
                    highlight_moves(selected_figure);
                }
            } else {
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
                    if (current_player === 'white') {
                        current_player = 'black';
                    } else {
                        current_player = 'white';
                    }
                    document.getElementById("game_state").textContent = current_player + ' turn';
                    show_board(chess_field);
                    if (chess_json["victory"] !== null) {
                        is_in_progress = false
                        document.getElementById("game_state").textContent = String(chess_json["victory"]["color"]) + " won!";
                        alert(String(chess_json["victory"]["color"]) + " won!");
                    }
                    run_chess_updater();
                } else {
                    dehighlight_moves(selected_figure);
                    selected_figure = null;
                    move_first = null;
                    move_second = null;
                }
            }

        });
    }
}
async function run_chess_updater() {
    let response_json = null;
    do {
        response_json = await send("chessInfo", JSON.stringify({"request": 'update_board', "user_color": user_color}));
    } while (response_json["request"] === "reject");
    chess_json = response_json;
    chess_update();
}
function chess_update() {
    if (chess_json.hasOwnProperty("error")) {
        return -1;
    }
    chess_field = chess_json["field"];
    chess_players = chess_json["players"];
    if (current_player === 'white') {
        current_player = 'black';
    } else {
        current_player = 'white';
    }
    document.getElementById("game_state").textContent = current_player + ' turn';
    show_board(chess_field);
    if (chess_json["victory"] !== null) {
        is_in_progress = false
        document.getElementById("game_state").textContent = String(chess_json["victory"]["color"]) + " won!";
        alert(String(chess_json["victory"]["color"]) + " won!");
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
       show_board(chess_field);

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
get_user_color()
    .then(() => init())
    .then(() => after_init());
