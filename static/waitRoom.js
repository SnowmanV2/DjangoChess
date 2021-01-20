
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
    return await send_to_server.json()
}
let players_in_room = null
async function init() {
    while(true) {
        console.log('before promise')
        let response_json = await send("waitRoom", JSON.stringify({"request": "start"}))
            console.log('response:' + response_json);
            if (response_json["start"] === "success") {
                console.log('If statement');
                window.location.replace(response_json["href"]);
                return 1;
            }
    }
}
init()

