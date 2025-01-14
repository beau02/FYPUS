document.getElementById('chatForm').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent default form submission

    const messageInput = document.getElementById('chatInput');
    const message = messageInput.value;
    if (!message.trim()) return; // Do nothing if input is empty

    // Display the user's message in the chat
    displayMessage('User: ' + message);

    // Clear the input field
    messageInput.value = '';

    // Send the message to the chatbot view via AJAX
    fetch("{% url 'chat' %}", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            'message': message
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to fetch');
        }
        return response.json();
    })
    .then(data => {
        if (data.response) {
            // Display the bot's response in the chat
            displayMessage('Bot: ' + data.response);
        } else {
            displayMessage('Bot: Sorry, something went wrong.');
        }
    })
    .catch(error => {
        displayMessage('Bot: Error connecting to the server.');
        console.error(error);
    });
});

// Function to display messages in the chat
function displayMessage(message) {
    const chatMessages = document.getElementById('chatMessages');
    const messageElement = document.createElement('li');
    messageElement.textContent = message;
    chatMessages.appendChild(messageElement);

    // Scroll to the bottom of the chat container
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
