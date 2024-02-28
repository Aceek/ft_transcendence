import { initializeSocket, messageHandler } from './socket.js';
import { Player } from './player.js';
import { Game } from './game.js';

console.log("Pong.js is executed!");

// ----------------------INITIALIZATION------------------------------------

var canvas = document.getElementById('pongCanvas');
var ctx = canvas.getContext('2d');

const game = new Game();
game.addPlayer(new Player(1, 'left', 0, 0, 0, 0, 0));
game.addPlayer(new Player(2, 'right', 0, 0, 0, 0, 0));

const socket = initializeSocket();
messageHandler(socket, game);

//----------------------KEY EVENT-----------------------------------------

// Event listeners for key presses
document.addEventListener("keydown", function (event) {
  console.log("Key down:", event.key);
  handleKeyPress(event.key, true);
});

document.addEventListener("keyup", function (event) {
  console.log("Key up:", event.key);
  handleKeyPress(event.key, false);
});

function handleKeyPress(key, isPressed) {
  console.log(`Key Event: ${key}, Pressed: ${isPressed}`);

  if (!isPressed || game.status != 1) {
      return;
  }

  if (!game.controlledPlayer) {
      console.log("Controlled player not found, exiting handleKeyPress");
      return;
  }

  if (key === "Enter" && game.gameStatus === 3 && isPressed) {
      console.log("Enter pressed to restart game");
      socket.send(JSON.stringify({ type: "restart_game" }));
      return;
  }

  let change = game.controlledPlayer.paddleSpeed;
  console.log(`Key pressed: ${key}, Current paddleY: ${game.controlledPlayer.paddleY}, Speed change: ${change}`);
  
  let newY = game.controlledPlayer.paddleY + (key === "ArrowDown" ? change : -change);
  console.log(`Calculated newY: ${newY}`);
  
  if (newY >= 0 && (newY + game.controlledPlayer.paddleHeight) <= canvas.height) {
      console.log(`Updating paddle position: ${newY} for ${game.controlledPlayer.side} paddle`);
      game.controlledPlayer.paddleY = newY;
      sendPaddlePositionUpdate(game.controlledPlayer);
  } else {
      console.log(`New position out of bounds: ${newY}, not updating. Current canvas height: ${canvas.height}`);
  }
  
}

let lastSentPaddleY = null;

function sendPaddlePositionUpdate(player) {
  if (lastSentPaddleY !== player.paddleY) {
      console.log(`Sending paddle position update for ${player.side}: ${player.paddleY}`);
      socket.send(JSON.stringify({
          type: "paddle_position_update",
          side: player.side,
          PaddleY: player.paddleY,
      }));
      lastSentPaddleY = player.paddleY;
  } else {
      console.log("No significant change in paddle position. Not sending update.");
  }
}

//----------------------MAIN LOOP-----------------------------------------

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
	 
   	if (game.status == 1) {
		game.ball.x = interpolatePosition(game.ball.x, game.ball.vx, deltaTime);
		game.ball.y = interpolatePosition(game.ball.y, game.ball.vy, deltaTime);
	  }

	  draw();

	  lastUpdateTime = timestamp - (deltaTime % frameDuration); // Adjust for any overshoot of the frame duration
	}
  
	requestAnimationFrame(mainLoop);
}
  
requestAnimationFrame(mainLoop); // Start the game loop

//----------------------DRAW-----------------------------------------

function draw() {
  // Clear the canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw each player's paddle
  game.players.forEach(player => {
      const x = player.side === 'left' ? 0 : canvas.width - player.paddleWidth;
      drawPaddle(x, player.paddleY, player.paddleWidth, player.paddleHeight);
  });

  // Draw the ball
  drawBall(game.ball.x, game.ball.y);

  // Draw the white dash line in the middle
  drawWhiteDashLine();

  // Draw scores for each player
  drawScores();

  if (game.status == 2) {
      console.log("waiting players");
      drawWaitingMessage();
  }

  if (game.status == 3) {
      drawGameOverMessage();
  }

  if (game.countdown !== null && game.countdown > 0) {
      ctx.font = "48px Arial";
      ctx.fillStyle = "red";
      ctx.textAlign = "center";
      ctx.fillText(game.countdown.toString(), canvas.width / 2, canvas.height / 2);
  }
}

function drawPaddle(x, y, paddleWidth, paddleHeight) {
  ctx.fillStyle = "#fff";
  ctx.fillRect(x, y, paddleWidth, paddleHeight);
}

function drawBall(x, y) {
  // console.log(`GS : ${game.status} - Drawing ball position - X: ${x.toFixed(2)}, Y: ${y.toFixed(2)}`);
  ctx.fillStyle = "#fff";
  ctx.fillRect(
    x - game.ball.size / 2,
    y - game.ball.size / 2,
    game.ball.size,
    game.ball.size
  );
}

function drawWhiteDashLine() {
  ctx.strokeStyle = "#fff";
  ctx.setLineDash([5, 5]);
  ctx.beginPath();
  ctx.moveTo(canvas.width / 2, 0);
  ctx.lineTo(canvas.width / 2, canvas.height);
  ctx.stroke();
  ctx.setLineDash([]);
}

function drawScores() {
  ctx.fillStyle = "#fff";
  ctx.font = '100px "Geo", sans-serif';
  const distanceFromCenter = 50;

  game.players.forEach((player, index) => {
      const textWidth = ctx.measureText(player.score).width;
      const x = player.side === 'left' ? (canvas.width / 2) - distanceFromCenter - textWidth
                                       : (canvas.width / 2) + distanceFromCenter;
      const y = canvas.height / 6;

      ctx.fillText(player.score, x, y);
  });
}

function drawGameOverMessage() {
  ctx.fillStyle = "#fff";
  ctx.font = '100px "Geo", sans-serif';

  let gameOverText = "Game Over!";
  let gameOverTextWidth = ctx.measureText(gameOverText).width;

  // Calculate the position for the game over message centered on the canvas
  let middleDashLineX = canvas.width / 2;
  let gameOverTextX = middleDashLineX - gameOverTextWidth / 2;

  // Set the height position slightly above the middle of the canvas
  let heightPosition = canvas.height / 2;

  // Draw the "Game Over" text
  ctx.fillText(gameOverText, gameOverTextX, heightPosition);

  // Adjust font size for the restart message
  ctx.font = '50px "Geo", sans-serif';
  let restartText = "Press Enter to restart";
  let restartTextWidth = ctx.measureText(restartText).width;
  let restartTextX = middleDashLineX - restartTextWidth / 2;

  // Draw the restart message slightly below the "Game Over" message
  ctx.fillText(restartText, restartTextX, heightPosition + 70); // Adjust vertical spacing for visibility
}

function drawWaitingMessage() {
 ctx.fillStyle = "#FFF";
  ctx.font = '30px Arial';
  ctx.textAlign = "center";
  ctx.fillText("Waiting for other players...", canvas.width / 2, canvas.height / 2);
}
