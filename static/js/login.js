function startLogin() {
    let username = document.getElementById('username_input').value;
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
                // window.location.pathname = "../../similar_user";
                const currentUrl = window.location.href;
                window.location.href = currentUrl + 'self_listening/' + username;
            }
        });
}