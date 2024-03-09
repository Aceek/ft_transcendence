function constructSocketUrl() {
    const { hostname, port, pathname } = window.location;
    const pathSegments = pathname.split('/').filter(Boolean);
    const [mode, playerNb, type, roomId] = pathSegments.slice(1);

    return `wss://${hostname}${port ? `:${port}` : ''}/ws/pong/${mode}/${playerNb}/${type}/${roomId}/`;
}

export function initializeSocket() {
    return new Promise((resolve, reject) => {
        const socketUrl = constructSocketUrl();
        console.log(socketUrl);

        const socket = new WebSocket(socketUrl);

        socket.addEventListener('open', () => {
            console.log("WebSocket connection opened");
            resolve(socket);
        });

        socket.addEventListener('error', (error) => {
            console.error("WebSocket error observed:", error);
            reject(error);
        });
    });
}

function handleWebSocketMessage(data, game) {
    switch (data.type) {
        case "game.static_data":
            game.handleStaticData(data.data);
            break;
        case "game.dynamic_data":
            game.handleDynamicData(data.data, data.timestamp);
            break;
        case "game.compacted_dynamic_data":
            game.handleCompactedDynamicData(data.ball, data.players, data.time);
            break;
        case "game.paddle_side":
            game.handlePaddleSideAssignment(data.paddle_side);
            break;
        case "game.countdown":
            game.handleCountdown(data.seconds);
            break;
        default:
            console.log("Unknown message type:", data.type);
    }
}

export function messageHandler(socket, game) {
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data, game);
    };
}
