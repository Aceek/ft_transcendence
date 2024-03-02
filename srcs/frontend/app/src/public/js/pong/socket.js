// socket.js

// Function to initialize the WebSocket connection
export function initializeSocket() {
    const hostname = window.location.hostname;
    const port = window.location.port;
    const roomID = window.location.pathname.split('/').pop();
    let socketUrl;

    if (port) {
        socketUrl = `wss://${hostname}:${port}/ws/pong/${roomID}/`;
    } else {
        socketUrl = `wss://${hostname}/ws/pong/${roomID}/`;
    }

	console.log("WebSocket curl", socketUrl);
    const socket = new WebSocket(socketUrl);

    socket.onopen = function(event) {
        console.log("WebSocket connection opened:", event);
    };

    socket.onclose = function(event) {
        console.log("WebSocket connection closed:", event);
    };

    // Return the socket to allow for further customization
    return socket;
}

// Function to set up WebSocket message handling
export function messageHandler(socket, game) {
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log("WebSocket message received:", data);

        switch (data.type) {
            case "game.static_data":
                game.handleStaticData(data.data); // Update to call method on game object
                break;
            case "game.dynamic_data":
                game.handleDynamicData(data.data, data.timestamp); // Update to call method on game object
                break;
            case "game.paddle_side":
                game.handlePaddleSideAssignment(data.paddle_side); // Update to call method on game object
                break;
            case "game.countdown":
                game.handleCountdown(data.seconds); // Update to call method on game object
                break;
            default:
                console.log("Unknown message type:", data.type);
        }
    };
}
