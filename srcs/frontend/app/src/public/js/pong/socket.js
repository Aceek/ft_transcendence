export function initializeSocket() {
    return new Promise((resolve, reject) => {
        const hostname = window.location.hostname;
        const port = window.location.port;

        const pathSegments = window.location.pathname.split('/').filter(Boolean);

        const mode = pathSegments[1];
        const playerNb = pathSegments[2];
        const gameType = pathSegments[3];
        const roomId = pathSegments[4];

        let socketUrl;
            
        socketUrl = `wss://${hostname}${port ? ':' + port : ''}/ws/pong/` +
                        `${mode}/${playerNb}/${gameType}/${roomId}/`;

        console.log(socketUrl);

        const socket = new WebSocket(socketUrl);

        socket.addEventListener('open', () => {
            console.log("WebSocket connection opened");
            resolve(socket); // Resolve the promise with the socket when it's open
        });

        socket.addEventListener('error', (error) => {
            console.error("WebSocket error observed:", error);
            reject(error); // Reject the promise on error
        });
    });
}


// Function to set up WebSocket message handling
export function messageHandler(socket, game) {
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        // console.log("WebSocket message received:", data);

        switch (data.type) {
            case "game.static_data":
                game.handleStaticData(data.data); // Update to call method on game object
                break;
            case "game.dynamic_data":
                game.handleDynamicData(data.data, data.timestamp); // Update to call method on game object
                break;
            case "game.compacted_dynamic_data":
                // Handler for compacted dynamic data, passing ball data, player data, and timestamp
                game.handleCompactedDynamicData(data.ball, data.players, data.time);
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
