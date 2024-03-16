import { initializeSocket, messageHandler } from './socket.js';
import { KeyEventController } from './keyEventController.js';
import { Renderer } from './renderer/renderer.js';
import { Game } from './game.js';

export let pongSocket;
let game;
let renderer;

export async function setupGame() {
    console.log("Pong.js is executed!");
    const canvas = document.getElementById('pongCanvas');
    if (!canvas) {
        console.error("Canvas element not found");
        return;
    }
    const ctx = canvas.getContext('2d');

    game = new Game();
    renderer = new Renderer(ctx, game);

    try {
        pongSocket = await initializeSocket();
        messageHandler(pongSocket, game);
        startSendingPing();

        new KeyEventController(pongSocket, game);

        waitForInitialization().then(() => {
            canvas.style.display = 'block'; // Make the canvas visible after initialization
            requestAnimationFrame(mainLoop);
        });
    } catch (error) {
        console.error("Failed to initialize WebSocket:", error);
    }
}

function startSendingPing() {
    setInterval(() => {
        if (pongSocket.readyState === WebSocket.OPEN) {
            pongSocket.send(JSON.stringify({
                type: "ping",
                timestamp: Date.now()
            }));
        }
    }, 100);
}

function waitForInitialization() {
    return new Promise(resolve => {
        const checkInitialization = () => {
            if (game.isInitialized) {
                resolve();
            } else {
                setTimeout(checkInitialization, 100);
            }
        };
        checkInitialization();
    });
}

//-----------------------------MAIN LOOP------------------------------------

function interpolatePosition(lastPosition, speed, deltaTime) {
    return lastPosition + speed * (deltaTime / 1000);
}

let lastFrameTime = Date.now();
let displayedFps = 0;
const alpha = 0.1;

function updateDisplayedFps(game, fps) {
    if(!game) {
        return;
    }
    displayedFps = alpha * fps + (1 - alpha) * displayedFps;
    game.fps = Math.round(displayedFps);
}

function mainLoop() {
    const now = Date.now();
    const deltaTime = now - lastFrameTime;

    if (deltaTime > 0) {
        const instantFps = 1000 / deltaTime;
        updateDisplayedFps(game, instantFps);
    }
    
    if (game && game.status === 1) {
        const gameDeltaTime = now - game.ball.lastServerUpdate;
        game.ball.x = interpolatePosition(game.ball.lastServerX, game.ball.vx, gameDeltaTime);
        game.ball.y = interpolatePosition(game.ball.lastServerY, game.ball.vy, gameDeltaTime);
        // console.log("Interpolation Ball:");
        // console.log("X:", game.ball.x, "Y:", game.ball.y);
    }

    renderer && renderer.draw();

    lastFrameTime = Date.now();

    requestAnimationFrame(mainLoop);
}

requestAnimationFrame(mainLoop);

