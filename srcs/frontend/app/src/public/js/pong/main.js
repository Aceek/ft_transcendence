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
const fps = 120;
const frameDuration = 1000 / fps;

function interpolatePosition(lastPosition, speed, deltaTime) {
  // Calculate and return the new position based on the speed and the delta time
  return lastPosition + speed * (deltaTime / 1000); // Convert deltaTime from ms to seconds
}

function mainLoop(timestamp) {
	const deltaTime = timestamp - lastUpdateTime;
  
	if (deltaTime > frameDuration) {
	 
   	if (game.status === 1) {
      game.ball.x = interpolatePosition(game.ball.x, game.ball.vx, deltaTime);
      game.ball.y = interpolatePosition(game.ball.y, game.ball.vy, deltaTime);
	  }

	  renderer.draw();

	  lastUpdateTime = timestamp - (deltaTime % frameDuration);
	}
  
	requestAnimationFrame(mainLoop);
}
  
requestAnimationFrame(mainLoop); // Start the game loop
