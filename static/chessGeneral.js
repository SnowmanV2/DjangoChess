export const numbers_to_literals = {
    "1": "a",
    "2": "b",
    "3": "c",
    "4": "d",
    "5": "e",
    "6": "f",
    "7": "g",
    "8": "h"
    };
export const literals_to_numbers = {
    "a": 1,
    "b": 2,
    "c": 3,
    "d": 4,
    "e": 5,
    "f": 6,
    "g": 7,
    "h": 8
}
export const static_figure_root = "/static/images/chessFigures/wikipedia/"
export const figure_to_link = {
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

export const items = document.getElementsByClassName("chessCell");

export function show_board(board) {
    let chess_field = board;
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
export function highlight_moves(figure) {
    figure["moves_available"].forEach(function(item) {
        let position_y = item[1];
        let position_x = item[0];
        let id = position_to_id(position_x, position_y);
        // items.namedItem(id).textContent = 'You can move here! ^^';
        items.namedItem(id).style.backgroundColor = '#85d6a0';
    })
}
export function dehighlight_moves(figure) {
    figure["moves_available"].forEach(function(item) {
        let position_y = item[1];
        let position_x = item[0];
        let id = position_to_id(position_x, position_y);
        // items.namedItem(id).textContent = '';
        items.namedItem(id).style.backgroundColor = null;
    })
}
export function id_to_position(id) {
    return {"position_x": literals_to_numbers[id[0]] - 1,
            "position_y": 8 - Number(id[1])};
}
export function position_to_id(x_position, y_position) {
    return numbers_to_literals[String(x_position + 1)] + String(8 - y_position);
}
export function is_figure_on_cell(players, x_position, y_position) {
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
export function has_coordinates(moves_available, x_position, y_position) {
    return moves_available.some(function(item) {
        return item['0'] === x_position && item['1'] === y_position;
    })
}
export function set_next_player(current_player) {
    if (current_player === 'white') {
        current_player = 'black';
    }
    else {
        current_player = 'white';
    }
}
