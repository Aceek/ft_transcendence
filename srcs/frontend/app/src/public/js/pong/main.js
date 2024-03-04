import { initializeSocket, messageHandler } from './socket.js';
import { KeyEventController } from './keyEventController.js';
import { GameRenderer } from './gameRenderer.js';
import { Game } from './game.js';

console.log("Pong.js is executed!");

// --------------------------------INIT------------------------------------

const canvas = document.getElementById('pongCanvas');
const ctx = canvas.getContext('2d');

const game = new Game();

const renderer = new GameRenderer(ctx, game);

const socket = initializeSocket();
messageHandler(socket, game);

new KeyEventController(socket, game);

//-----------------------------MAIN LOOP------------------------------------

function interpolatePosition(lastPosition, speed, deltaTime) {
    // Calculate and return the new position based on the speed and the delta time
    return lastPosition + speed * (deltaTime / 1000); // Convert deltaTime from ms to seconds
}

let lastUpdate = Date.now()
let delta = 0

function mainLoop() {
    delta = Date.now() - lastUpdate;

    if (game.status === 1) {
        // Interpolate position only if shouldInterpolate is true
        game.ball.x = interpolatePosition(game.ball.x, game.ball.vx, delta);
        game.ball.y = interpolatePosition(game.ball.y, game.ball.vy, delta);

        // console.log("Interpolated Ball position - X:", game.ball.x, "Y:", game.ball.y);
    }

    lastUpdate = Date.now();

    renderer.draw();
    requestAnimationFrame(mainLoop);
}

// Start the game loop
requestAnimationFrame(mainLoop);
