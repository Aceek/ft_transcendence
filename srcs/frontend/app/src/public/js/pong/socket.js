function constructSocketUrl() {
    const { hostname, port, pathname } = window.location;
    const pathSegments = pathname.split('/').filter(Boolean);
    const [mode, playerNb, type, roomId] = pathSegments.slice(1);

    if (!mode || !playerNb || !type || !roomId) {
        console.error("Invalid WebSocket URL: Missing parameters");
        return null;
    }

    return `wss://${hostname}${port ? `:${port}` : ''}/ws/pong/${mode}/${playerNb}/${type}/${roomId}/`;
}

export function initializeSocket(game) {
    return new Promise((resolve, reject) => {
        const socketUrl = constructSocketUrl();
        
        if (!socketUrl) {
            reject(new Error("Failed to initialize WebSocket: Invalid URL"));
            return;
        }
        
        const socket = new WebSocket(socketUrl);

        socket.addEventListener('open', () => {
            console.log("WebSocket connection opened");
            resolve(socket);
        });

        socket.addEventListener('error', (error) => {
            console.error("WebSocket error observed:", error);
            reject(error);
        });

        socket.addEventListener('close', (event) => {
            const reason = event.reason ? ` Reason: ${event.reason}` : '';
            console.log(`WebSocket connection closed with code: ${event.code}.${reason}`);
        
            if (event.code === 1006) {
                game.status = 4;
            } else if (event.code === 1012) {
                game.status = 5;
            }
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
            game.handleCompactedDynamicData(data.ball, data.players, data.processTime);
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
        if (data.type == "pong") {
            game.latency = (Date.now() - data.timestamp) / 2;
        } else {
            handleWebSocketMessage(data, game);
        }
    };
}
