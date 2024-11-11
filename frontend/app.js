document.getElementById("queryInput").addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();  // Prevent form submission or default actions
        submitQuery();           // Call the submit function
    }
});

async function submitQuery() {
    const queryInput = document.getElementById("queryInput");
    const chatWindow = document.getElementById("chatWindow");
    const userMessage = queryInput.value.trim();

    if (!userMessage) return;

    // Add user message to the chat window
    const userBubble = document.createElement("div");
    userBubble.className = "chat-bubble user";
    userBubble.innerText = userMessage;
    chatWindow.appendChild(userBubble);
    queryInput.value = "";  // Clear the input

    // Scroll to the bottom
    chatWindow.scrollTop = chatWindow.scrollHeight;

    // Show loading message
    const botBubble = document.createElement("div");
    botBubble.className = "chat-bubble bot";
    botBubble.innerText = "Loading...";
    chatWindow.appendChild(botBubble);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    try {
        const response = await fetch("http://127.0.0.1:5001/submit_query", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query: userMessage })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        botBubble.innerText = data.response ? data.response : "No relevant results found.";
    } catch (error) {
        botBubble.innerText = "Error fetching results.";
        console.error("Error:", error);
    }

    // Scroll to the bottom again after response
    chatWindow.scrollTop = chatWindow.scrollHeight;
}
