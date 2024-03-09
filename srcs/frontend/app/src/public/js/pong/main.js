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
    // Calculate and return the new position based on the speed and the delta time
    return lastPosition + speed * (deltaTime / 1000);
}

function mainLoop() {
    if (game && game.status === 1) {
        let now = Date.now();
        let deltaTime = now - game.ball.lastServerUpdate;

        game.ball.x = interpolatePosition(game.ball.lastServerX, game.ball.vx, deltaTime);
        game.ball.y = interpolatePosition(game.ball.lastServerY, game.ball.vy, deltaTime);

        // Reset this value if the game is restart
        if (game.restartRequest) {
            game.restartRequest = false;
        }
    }

    renderer && renderer.draw();
    requestAnimationFrame(mainLoop);
}

