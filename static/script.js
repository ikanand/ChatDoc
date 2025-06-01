const chatBox = 
    document.getElementById('chat-box');
const userInput = 
    document.getElementById('user-input');
const sendButton = 
    document.getElementById('send-button');
const sidebarToggle = 
    document.getElementById('sidebar-toggle');
const modeToggle = 
    document.getElementById('mode-toggle-checkbox');
const sidebar = 
    document.querySelector('.sidebar');

sendButton.addEventListener('click', async () => {
    await sendMessage(); // Ensure the async function is called correctly
});



document.addEventListener('DOMContentLoaded', function () {
    const newConversationBtn = 
            document.getElementById('new-conversation-btn');
    const viewCollectionBtn = 
            document.getElementById('view-collection-btn');
    const conversationContent = 
            document.querySelector('.conversation-content');
    const sidebarToggle = 
            document.getElementById('sidebar-toggle');
    const chatContainer = 
            document.querySelector('.chat-container');
    const sidebar = 
            document.querySelector('.sidebar');
    

    // Ensure the sidebar is expanded by default on load
    sidebar.classList.remove('collapsed');
    chatContainer.style.width = 'calc(100% - 300px)';
    chatContainer.style.marginLeft = '300px';

    // Add event listener for the toggle button
    sidebarToggle.addEventListener('click', function () {
        sidebar.classList.toggle('collapsed');

        if (sidebar.classList.contains('collapsed')) {
            chatContainer.style.width = '96%';
            chatContainer.style.marginLeft = '3%';
        } else {
            chatContainer.style.width = 'calc(100% - 300px)';
            chatContainer.style.marginLeft = '300px';
        }
    });

    // Add event listener for the new conversation button
    newConversationBtn.addEventListener('click', function () {
        window.location.href = '/';
        loadConversations(); // Reload conversations when a new conversation is started
    });

    // Add event listener for the view CollectionBtn button
    viewCollectionBtn.addEventListener('click', function () {
        window.open('/collection', '_blank');
        
    });

});

document.addEventListener('DOMContentLoaded', function () {
    const messageInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Allow Shift + Enter for new lines
    messageInput.addEventListener('keydown', function (event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendButton.click(); // Programmatically click the "Send" button
        }
    });

    // Optional: Dynamically adjust textarea height based on content
    messageInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px'; // Limit height to 120px
    });


});

async function loadConversation(existingConvId) {
    convId = existingConvId;

    try {
        const response = await fetch(`/message/${convId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: '' }) // Ping with an empty message to retrieve history
        });

        const data = await response.json();
        if (data.history) {
            chatBox.innerHTML = ''; // Clear the chat box
            data.history.forEach(entry => {
                appendMessage(entry.type === 'user' ? 'user' : 'ChatGPT', entry.content);
            });
        }
    } catch (err) {
        appendMessage('ChatGPT', `Error: Failed to load the session. ${err.message}`);
    }
}

let convId = null; // Global variable to track the conversation ID

async function sendMessage() {
    
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();
    const sendButton = document.getElementById('send-button');
    const sendIcon = sendButton.querySelector('i'); // Get the send plane icon
    const spinner = document.getElementById('send-spinner'); // Get the spinner element

    if (message !== '') {
        appendMessage('user', message); // Add user input to the chat UI
        console.log('!Sending message:', message);
        console.log('!Current convId:', convId);

        sendIcon.style.display = 'none';
        spinner.style.display = 'block';

        try {
            // Make the API call asynchronously
            const response = await fetch(`/message/${convId || 'null'}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message }) // Send the user's input
            });
            console.log('!response:', response);

            let data; // Variable to store parsed body
            try {
                // Attempt to parse the JSON response
                data = await response.json();
                console.log('!data:', data);
            } catch (err) {
                // Handle JSON parsing errors
                console.error('Failed to parse response JSON:', err);
                appendMessage('ChatGPT', `Error: Unable to read response from the server.`);
                return;
            }finally {
        // Restore the send icon and hide the spinner
        sendIcon.style.display = 'block';
        spinner.style.display = 'none';
    }

            if (response.ok) {
                console.log('Backend response:', data);

                // Store the conversation ID for the current session
                convId = data.conv_id;
                console.log('Updated convId:', convId);

                // Display the LLM response
                appendMessage('ChatGPT', data.response);
            } else {
                // Handle API errors and show the error message in the chat UI
                console.error('Backend error response:', data);
                appendMessage('ChatGPT', `Error: ${data.message || 'Something went wrong.'} ${data.error || ''}`);
            }

        } catch (err) {
            // Handle network-related errors (e.g., unable to connect to the backend)
            console.error('Connection error:', err);
            appendMessage('ChatGPT', `Error: Failed to communicate with the backend. ${err.message}`);
        }

        // Clear the input field
        userInput.value = '';
    }
}


function appendMessage(sender, message) {
    
    const p = document.createElement('p');
    p.textContent = sender === 'user' ? `🤵: ${message}` : `🤖: ${message}`;
    p.classList.add(sender === 'user' ? 'user-message' : 'llm-message');

    

    chatBox.appendChild(p);
    chatBox.scrollTop = chatBox.scrollHeight; // Keep chat scrolled to the bottom
}



function getCurrentTime() {
    const now = new Date();
    return `Current time is ${now.toLocaleTimeString()}`;
}

function getCurrentDate() {
    const now = new Date();
    return `Today's date is ${now.toDateString()}`;
}

function getWeatherInfo() {

    // Simulate getting weather information from an API
    const weatherData = {
        temperature: getRandomNumber(10, 35),
        condition: getRandomElement(["Sunny", "Cloudy", "Rainy", "Windy"]),
    };
    return `Current weather: ${weatherData.temperature}°C,
                             ${weatherData.condition}`;
}

function getJoke() {
    
    // Simulate getting a random joke
    const jokes = ["Why don't scientists trust atoms? Because they make up everything!",
        "Parallel lines have so much in common. It's a shame they'll never meet.",
        "I told my wife she was drawing her eyebrows too high. She looked surprised.",
        "Why did the scarecrow win an award? Because he was outstanding in his field!"
    ];
    return getRandomElement(jokes);
}

function getFact() {
    
    // Simulate getting a random fact
    const facts = ["Ants stretch when they wake up in the morning.", 
                   "A group of flamingos is called a flamboyance.",
                   "Honey never spoils.",
                   "The shortest war in history lasted only 38 minutes.",
                   "Octopuses have three hearts."
    ];
    return getRandomElement(facts);
}

function getQuote() {
    
    // Simulate getting a random quote
    const quotes = 
        ["The only way to do great work is to love what you do. – Steve Jobs",
        "In the middle of difficulty lies opportunity. – Albert Einstein",
        "Success is not final, failure is not fatal: It is the courage to continue that counts. – Winston Churchill"
    ];
    return getRandomElement(quotes);
}

function getRandomElement(array) {
    const randomIndex = Math.floor(Math.random() * array.length);
    return array[randomIndex];
}

function getRandomNumber(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}


async function loadConversations() {
  const conversationsList = document.getElementById('conversations-list');

  try {
    const response = await fetch(`/get_conversations`);
    const data = await response.json();

    // Clear the placeholder content
    conversationsList.innerHTML = '';

    if (data && data.length > 0) {
      // Loop through the conversations and create a UI element for each
      data.forEach(conversation => {
        const conversationItem = document.createElement('div');
        conversationItem.textContent = `${conversation.first_question}`;
        conversationItem.classList.add('conversation-item');
        conversationItem.setAttribute('data-id', conversation.id);

        // Add click handler to open the conversation when clicked
        conversationItem.addEventListener('click', () => {
            const previousActiveItem = conversationsList.querySelector('.conversation-item.active');
            if (previousActiveItem) {
                previousActiveItem.classList.remove('active');
                }

          // Add 'active' class to the clicked conversation
          conversationItem.classList.add('active');


          loadConversationHistory(conversation.id);
        });

        conversationsList.appendChild(conversationItem);
      });
    } else {
      // If no conversations are available, show a placeholder message
      conversationsList.innerHTML = '<p class="conversation-content">No conversations available.</p>';
    }
  } catch (err) {
    console.error('Error fetching conversations:', err);
    conversationsList.innerHTML = '<p class="conversation-content">Error loading conversations</p>';
  }
}

// Function to fetch and render the chat history for a specific conversation
async function loadConversationHistory(conv_id) {
  const chatBox = document.getElementById('chat-box');

  try {
    const response = await fetch(`/message/${conv_id}`);
    const data = await response.json();
    convId = conv_id; // Update the global conversation ID
   console.log('Updated the convID:', convId);
    // Clear the chat box and add new messages
    chatBox.innerHTML = '';
    if (data && data.messages && data.messages.length > 0) {
      data.messages.forEach(message => {
        const messageElement = document.createElement('div');

         
        if (message.type === 'human') {
            messageElement.textContent = `🤵 :  ${message.content}`;
            messageElement.classList.add('user-message');
        } else {
            messageElement.textContent = `🤖 : ${message.content}`;
            messageElement.classList.add('llm-message');
        }
        chatBox.appendChild(messageElement);
      });
    } else {
      chatBox.innerHTML = '<p>No messages in this conversation</p>';
    }
  } catch (err) {
    console.error('Error fetching conversation history:', err);
    chatBox.innerHTML = '<p>Error loading messages</p>';
  }
}

// Load conversations when the page loads
window.onload = loadConversations;