window.onload = function() {
    document.getElementById("large-title").style.setProperty("opacity", "1");
    document.getElementById("large-title").style.setProperty("transform", "none");
    document.getElementById("medium-title").style.setProperty("opacity", "1");
    document.getElementById("medium-title").style.setProperty("transform", "none");
    document.getElementById("username-input").style.setProperty("opacity", "1");
    document.getElementById("username-input").style.setProperty("transform", "none");
    document.getElementById("b-color").style.setProperty("opacity", "1");
}

function startLogin() {
    let username = document.getElementById('username_input').value;
    let mode = document.getElementById('mode_select').value;
    if (username === "") {
        document.getElementById('username_input').placeholder = "No username!";
    }
    fetch(`/check_user/${username}`)
        .then(response => response.json())
        .then(data => {
            if (data == false){
                document.getElementById('username_input').value = ""
                document.getElementById('username_input').placeholder = "Username not found :("
            } else {
                document.getElementById("b-color-pink").style.setProperty("z-index", "10");
                document.body.style.setProperty("background", "rgb(225, 211, 230)");
                document.getElementById("b-color").style.setProperty("opacity", "0");
                document.getElementById("b-color-pink").style.setProperty("opacity", "1");
                setTimeout(function()
                    {
                        const currentUrl = window.location.href;
                        window.location.href = currentUrl + mode + '/' + username;
                    }, 3000);
            }
        });
}