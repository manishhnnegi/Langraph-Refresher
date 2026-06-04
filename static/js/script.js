let waitingForApproval = false;

function addMessage(text, sender) {

    const div = document.createElement("div");

    div.className = sender;

    div.innerHTML =
        `<span class="bubble">${text}</span>`;

    document
        .getElementById("messages")
        .appendChild(div);
}

async function sendMessage() {

    const input =
        document.getElementById("message-input");

    const message = input.value;

    input.value = "";

    addMessage(message, "user");

    const response = await fetch(
        "http://localhost:8000/chat",
        {
            method: "POST",
            headers: {
                "Content-Type":
                    "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        }
    );

    const data = await response.json();

    if (data.type === "message") {

        addMessage(
            data.message,
            "bot"
        );
    }

    if (data.type === "interrupt") {

        document
            .getElementById("approval-box")
            .classList.remove("hidden");

        document
            .getElementById("approval-data")
            .textContent =
                JSON.stringify(
                    data.data,
                    null,
                    2
                );
    }
}




async function approve(value) {

    document
        .getElementById("approval-box")
        .classList.add("hidden");

    const response = await fetch(
        "http://localhost:8000/resume",
        {
            method: "POST",
            headers: {
                "Content-Type":
                    "application/json"
            },
            body: JSON.stringify({
                approved: value
            })
        }
    );

    const data = await response.json();

    addMessage(
        data.message,
        "bot"
    );
}