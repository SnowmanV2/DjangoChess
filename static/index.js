if(current_user_name === "None") {
    // document.getElementById("logout").style.visibility = "hidden";
    // document.getElementById("profile").style.visibility = "hidden";
    // document.getElementById("login").style.visibility = "visible";
    // document.getElementById("signup").style.visibility = "visible";
    document.getElementById("login").style.visibility = "visible";
    // document.getElementById("logged").style.visibility = "hidden";
    document.getElementById("logged").remove();
} else {
    console.log("Hi, " + current_user_name + "!");
    // document.getElementById("logout").style.visibility = "visible";
    // document.getElementById("profile").style.visibility = "visible";
    // document.getElementById("login").style.visibility = "hidden";
    // document.getElementById("signup").style.visibility = "hidden";
    document.getElementById("login").remove();
    // document.getElementById("login").style.visibility = "hidden";
    document.getElementById("logged").style.visibility = "visible";
}
document.getElementById("difficultyEasy").style.visibility = "hidden";
document.getElementById("difficultyMedium").style.visibility = "hidden";
document.getElementById("difficultyHard").style.visibility = "hidden";
document.getElementById("versusAiButton").addEventListener("click", function() {
    if(document.getElementById("difficultyEasy").style.visibility === "hidden") {
        document.getElementById("difficultyEasy").style.visibility = "visible";
        document.getElementById("difficultyMedium").style.visibility = "visible";
        document.getElementById("difficultyHard").style.visibility = "visible";
    } else {
        document.getElementById("difficultyEasy").style.visibility = "hidden";
        document.getElementById("difficultyMedium").style.visibility = "hidden";
        document.getElementById("difficultyHard").style.visibility = "hidden";
    }

})