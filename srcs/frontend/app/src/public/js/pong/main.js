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
    }, 200);
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

let frameCount = 0;
let lastFpsTime = Date.now();

function updateFps(now) {
    frameCount++;
    const delta = now - lastFpsTime;
    if (game && delta >= 1000) {
        game.fps = Math.round((frameCount / delta) * 1000);
        frameCount = 0;
        lastFpsTime = now;
    }
}

function mainLoop() {
    
    updateFps(Date.now());
    
    if (game && game.status === 1) {
        const gameDeltaTime = Date.now() - game.ball.lastServerUpdate;
        game.ball.x = interpolatePosition(game.ball.lastServerX, game.ball.vx, gameDeltaTime);
        game.ball.y = interpolatePosition(game.ball.lastServerY, game.ball.vy, gameDeltaTime);
    }

    renderer && renderer.draw();

    requestAnimationFrame(mainLoop);
}

requestAnimationFrame(mainLoop);
