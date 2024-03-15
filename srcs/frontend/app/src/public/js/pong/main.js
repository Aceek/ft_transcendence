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

        new KeyEventController(pongSocket, game);

        waitForInitialization().then(() => {
            canvas.style.display = 'block'; // Make the canvas visible after initialization
            requestAnimationFrame(mainLoop);
        });
    } catch (error) {
        console.error("Failed to initialize WebSocket:", error);
    }
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
    // Calculate and return the new position based on the speed and the deltaTime
    return lastPosition + speed * (deltaTime / 1000);
}

let lastFrameTime = Date.now();
let movingAverageFps = 0;
const alpha = 0.01; 

function updateFps(fps) {
    movingAverageFps = alpha * fps + (1 - alpha) * movingAverageFps;
    if (game && typeof game.fps !== 'undefined') {
        game.fps = Math.round(movingAverageFps);
    }
}

function mainLoop() {
    const now = Date.now();
    const deltaTime = now - lastFrameTime;

    if (game && game.status === 1) {
        const gameDeltaTime = now - game.ball.lastServerUpdate;
        // Update the ball position based on the last known velocity and the elapsed time since the last update
        game.ball.x = interpolatePosition(game.ball.lastServerX, game.ball.vx, gameDeltaTime);
        game.ball.y = interpolatePosition(game.ball.lastServerY, game.ball.vy, gameDeltaTime);
    }

    if (deltaTime > 0) {
        const instantFps = 1000 / deltaTime;
        updateFps(instantFps);
    }

    renderer && renderer.draw();

    lastFrameTime = now;

    requestAnimationFrame(mainLoop);
}

requestAnimationFrame(mainLoop);
