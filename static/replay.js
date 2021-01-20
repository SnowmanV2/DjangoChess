import {
    show_board
} from "/static/chessGeneral.js";

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
function set_next_player() {
    if (current_player === 'white') {
        current_player = 'black';
    }
    else {
        current_player = 'white';
    }
}
async function init() {
    chess_json = await send("", JSON.stringify({"command": "init"}));
    chess_field = chess_json["field"];
    current_player = "white"
    document.getElementById("game_state").textContent = current_player + ' turn';
    show_board(chess_field);
    await document.getElementById("previousButton").addEventListener("click", async function (e) {
        is_in_progress = false;
        let json_data = {
            "command": "previous"
        };
        let response_json = await send("", JSON.stringify(json_data));
        if (response_json["response"] === "success") {
            chess_field = response_json["field"];
            set_next_player()
            document.getElementById("game_state").textContent = current_player + ' turn';
            show_board(chess_field);
        }
    })
    await document.getElementById("nextButton").addEventListener("click", async function (e) {
        is_in_progress = false;
        let json_data = {
            "command": "next"
        };
        let response_json = await send("", JSON.stringify(json_data));
        if (response_json["victory"] !== undefined) {
            is_in_progress = false
            document.getElementById("game_state").textContent = String(response_json["victory"]) + " won!";
            alert(String(response_json["victory"]) + " won!");
        }
        if (response_json["response"] === "success") {
            chess_field = response_json["field"];
            show_board(chess_field);


            set_next_player()
            document.getElementById("game_state").textContent = current_player + ' turn';


        }
    })

}
init()
