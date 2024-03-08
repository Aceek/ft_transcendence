import { initializeSocket, messageHandler } from './socket.js';
import { KeyEventController } from './keyEventController.js';
import { GameRenderer } from './gameRenderer.js';
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
    renderer = new GameRenderer(ctx, game);

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
    return lastPosition + speed * (deltaTime / 1000); // Convert deltaTime from ms to seconds
}

function mainLoop() {
    let delta = Date.now() - lastUpdate;

    if (game && game.status === 1) {
        game.ball.x = interpolatePosition(game.ball.x, game.ball.vx, delta);
        game.ball.y = interpolatePosition(game.ball.y, game.ball.vy, delta);
    
        // Print the current ball position for debugging
        console.log(`Ball position - X: ${game.ball.x}, Y: ${game.ball.y}`);

        // reset this value if the game if the game is restart
        if (game.restartRequest == true) {
            game.restartRequest = false;
        }
    }

    lastUpdate = Date.now();
    renderer && renderer.draw();
    requestAnimationFrame(mainLoop);
}

let lastUpdate = Date.now()
