const API_URL = "http://localhost:8000";
let currentUser = localStorage.getItem("username");
let currentChat = null;

async function signup() {
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    await fetch(`${API_URL}/signup`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username, password})
    });

    alert("Signup successful!");
}

async function login() {
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    let response = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username, password})
    });

    if (response.ok) {
        localStorage.setItem("username", username);
        currentUser = username;
        document.getElementById("auth-container").style.display = "none";
        document.getElementById("chat-container").style.display = "block";
        loadFriendRequests();
    } else {
        alert("Invalid credentials");
    }
}

async function addFriend() {
    let friendUsername = document.getElementById("friend-username").value;

    await fetch(`${API_URL}/add-friend`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({sender: currentUser, receiver: friendUsername})
    });

    alert("Friend request sent!");
}

async function loadFriendRequests() {
    let response = await fetch(`${API_URL}/friend-requests/${currentUser}`);
    let requests = await response.json();

    let requestContainer = document.getElementById("friend-requests");
    requestContainer.innerHTML = "";

    requests.forEach(req => {
        let btn = document.createElement("button");
        btn.innerText = `Accept ${req.sender}`;
        btn.onclick = () => acceptFriend(req.id);
        requestContainer.appendChild(btn);
    });
}

async function acceptFriend(requestId) {
    await fetch(`${API_URL}/accept-friend/${requestId}`, { method: "POST" });
    alert("Friend added!");
    loadFriendRequests();
}

async function sendMessage() {
    let message = document.getElementById("message-input").value;

    await fetch(`${API_URL}/send`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({sender: currentUser, receiver: currentChat, content: message})
    });

    loadMessages();
}

async function loadMessages() {
    let response = await fetch(`${API_URL}/messages/${currentUser}/${currentChat}`);
    let messages = await response.json();

    let messageContainer = document.getElementById("messages");
    messageContainer.innerHTML = "";
    messages.forEach(msg => {
        let div = document.createElement("div");
        div.innerText = `${msg.sender}: ${msg.content}`;
        messageContainer.appendChild(div);
    });
}
