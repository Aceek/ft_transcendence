import { initializeSocket, messageHandler } from './socket.js';
import { KeyEventController } from './keyEventController.js';
import { GameRenderer } from './gameRenderer.js';
import { Player } from './player.js';
import { Game } from './game.js';

console.log("Pong.js is executed!");

// --------------------------------INIT------------------------------------

const canvas = document.getElementById('pongCanvas');
const ctx = canvas.getContext('2d');

const game = new Game();
game.addPlayer(new Player(1, 'left'));
game.addPlayer(new Player(2, 'right'));

const renderer = new GameRenderer(ctx, game);

const socket = initializeSocket();
messageHandler(socket, game);

new KeyEventController(socket, game);

//-----------------------------MAIN LOOP------------------------------------

let lastUpdateTime = 0;
const fps = 240;
const frameDuration = 1000 / fps;

function interpolatePosition(lastPosition, speed, deltaTime) {
    // Calculate and return the new position based on the speed and the delta time
    return lastPosition + speed * (deltaTime / 1000); // Convert deltaTime from ms to seconds
}

function mainLoop() {
    const now = Date.now(); // Get current time in milliseconds
    const timeSinceLastServerUpdate = now - game.lastServerUpdate; // Time since last server data was processed

    // Calculate deltaTime based on the last update time for consistent frame updates
    const deltaTime = now - lastUpdateTime;

    if (deltaTime >= frameDuration) {
        if (game.status === 1) {
            // Use timeSinceLastServerUpdate for interpolation to simulate movement since the last server update
            game.ball.x = interpolatePosition(game.ball.x, game.ball.vx, timeSinceLastServerUpdate);
            game.ball.y = interpolatePosition(game.ball.y, game.ball.vy, timeSinceLastServerUpdate);
        }

        // Print the ball's current position
        // console.log(`C - Ball position - X: ${game.ball.x}, Y: ${game.ball.y}`);

        renderer.draw();

        // Update lastUpdateTime to now, correcting for the frame overshoot, to maintain consistent FPS
        lastUpdateTime = now - (deltaTime % frameDuration);
    }

    requestAnimationFrame(mainLoop);
}

// Start the game loop
requestAnimationFrame(mainLoop);

