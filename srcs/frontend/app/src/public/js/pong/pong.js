// ----------------------INITIALIZATION------------------------------------

console.log("Pong.js is executed!");

var canvas = document.getElementById('pongCanvas');
var ctx = canvas.getContext('2d');
const hostname = window.location.hostname;
const port = window.location.port;
const roomID = window.location.pathname.split('/').pop();
let socketUrl;

// Check if port is available
if (port) {
    socketUrl = 'wss://' + hostname + ':' + port + '/ws/pong/' + roomID + '/';
} else {
    socketUrl = 'wss://' + hostname + '/ws/pong/' + roomID + '/';
}

var socket = new WebSocket(socketUrl);

//----------------------WEBSOCKET-----------------------------------------

socket.onopen = function (event) {
  console.log("WebSocket connection opened:", event);
};

socket.onmessage = function (event) {
  var data = JSON.parse(event.data);
//   console.log("WebSocket message received:", data);

  switch (data.type) {
    case "game.static_data":
      handleStaticData(data.data); // Handle static game data
      break;
    case "game.dynamic_data":
      handleDynamicData(data.data); // Handle dynamic game data
      break;
    case "game.paddle_side": // Handle paddle side assignment
      handlePaddleSideAssignment(data.paddle_side);
      break;
    case "game.score_update": // Handle score update
      handleScoreUpdate(data.side, data.score);
      break;
    case "game.status_update": // NEW: Handle game status update
      handleGameStatusUpdate(data.status);
      break;
    default:
      console.log("Unknown message type:", data.type);
  }
};

socket.onclose = function (event) {
  console.log("WebSocket connection closed:", event);
};

//----------------------EVENT LISTENERS-----------------------------------------

// Event listeners for key presses
document.addEventListener("keydown", function (event) {
  // console.log("Key down:", event.key);
  handleKeyPress(event.key, true);
});

document.addEventListener("keyup", function (event) {
  // console.log("Key up:", event.key);
  handleKeyPress(event.key, false);
});

function handleKeyPress(key, isPressed) {
  // Early exit if the paddle side is not set
  if (!game.paddle.side) {
    return;
  }
  
  // Determine the change in position
  let change = game.paddle.speed * (isPressed ? 1 : 0);
  
  // Select the correct paddle based on the assigned side
  let paddleKey = game.paddle.side === "left" ? "left" : "right";
  
  // Update paddle position based on the key pressed
  if (key === "ArrowUp") {
    game.players[paddleKey].paddleY -= change;
  } else if (key === "ArrowDown") {
    game.players[paddleKey].paddleY += change;
  }
  
  // Send position update
  sendPaddlePositionUpdate();
}

//----------------------GAME UPDATE----------------------------------------------

// Global variables to track the last sent paddle positions for both sides
let lastSentPaddleY = null;

function sendPaddlePositionUpdate() {
  // Determine the current player's paddle and the corresponding variable for tracking
  const isLeftSide = game.paddle.side === "left";
  const currentPlayer = isLeftSide ? game.players.left : game.players.right;
  // const lastSentPaddleY = isLeftSide ? lastSentLeftPaddleY : lastSentRightPaddleY;
  
  // Check if there's a significant change in the current paddle's position
  if (currentPlayer.paddleY !== lastSentPaddleY) {
    lastSentLeftPaddleY = currentPlayer.paddleY;
  }
  
  // Send updated position to the server
  socket.send(JSON.stringify({
    type: "paddle_position_update",
    side: game.paddle.side,
      PaddleY: currentPlayer.paddleY,
  }));

  console.log(`${game.paddle.side} paddle position sent:`, currentPlayer.paddleY);
}
  
// Function to handle paddle side assignment
function handlePaddleSideAssignment(paddleSide) {
  console.log("Assigned paddle side:", paddleSide);
  // Assign the paddle side to your game state
  game.paddle.side = paddleSide;
}

function handleScoreUpdate(side, score) {
  console.log(`Score update for ${side} side:`, score);
  
  // Assuming you have elements with IDs 'leftScore' and 'rightScore' to display scores
  if (side === "left") {
    game.players.left.score = score;
  } else if (side === "right") {
    game.players.right.score = score;
  }
}

function handleGameStatusUpdate(status) {
  console.log("Game status update received:", status);
  game.status = status;
}


//----------------------DATA INITALIZATION---------------------------------------

var game = {
  paddle: {
    width: 0,
    height: 0,
    side: null,
  },
  ball: {
    size: 0,
    x: 0,
    y: 0,
    speedX: 0,
    speedY: 0,
  },
  players: {
    left: {
      paddleY: 0,
      score: 0,
    },
    right: {
      paddleY: 0,
      score: 0,
    },
  },
  gameStatus: 0,
//   userID: null,
};

function handleStaticData(staticData) {
//   console.log("Received static data:", staticData);

  // Parse static game settings
  game.paddle.width = parseInt(staticData.paddleWidth, 10);
  game.paddle.height = parseInt(staticData.paddleHeight, 10);
  game.ball.size = parseInt(staticData.ballSize, 10);

  // Update canvas dimensions directly from staticData
  canvas.width = parseInt(staticData.canvasWidth, 10);
  canvas.height = parseInt(staticData.canvasHeight, 10);

  // Update other static game settings directly from staticData
  game.scoreLimit = parseInt(staticData.scoreLimit, 10);
  game.paddle.speed = parseInt(staticData.paddleSpeed, 10);

  // Log the updated game settings for debugging
//   console.log("Static game settings parsed and updated:", game);
}

function handleDynamicData(dynamicData) {
  // console.log("Handling dynamic data:", dynamicData);
  // Update the game state with parsed dynamic data
  game.ball.x = parseInt(dynamicData.b_x, 10);
  game.ball.y = parseInt(dynamicData.b_y, 10);
  game.ball.speedX = parseInt(dynamicData.bs_x, 10);
  game.ball.speedY = parseInt(dynamicData.bs_y, 10);
  game.players.left.paddleY = parseInt(dynamicData.lp_y, 10);
  game.players.right.paddleY = parseInt(dynamicData.rp_y, 10);

  // Log the updated game state for debugging
//   console.log("Updated game state with dynamic data:", game);
}

//----------------------GAME LOOP-----------------------------------------

let lastUpdateTime = 0;
const fps = 240;
const frameDuration = 1000 / fps;

function interpolatePosition(lastPosition, speed, deltaTime) {
  // Calculate and return the new position based on the speed and the delta time
  return lastPosition + speed * (deltaTime / 1000); // Convert deltaTime from ms to seconds
}

let isGamePaused = false;

function mainLoop(timestamp) {
  // Calculate the delta time since the last frame
  const deltaTime = timestamp - lastUpdateTime;

  
  if (deltaTime > frameDuration) {
    // Calculate the interpolated positions
    game.ball.x = interpolatePosition(game.ball.x, game.ball.speedX, deltaTime);
    game.ball.y = interpolatePosition(game.ball.y, game.ball.speedY, deltaTime);
    
    draw(); // Draw the frame with the interpolated positions
    
    if (game.status === "SUSPENDED") {
      drawPausedMessage();
      requestAnimationFrame(mainLoop); // Continue to request animation frames to check for status changes
      return; // Skip the rest of the loop logic
    }
  
    if (game.status === "COMPLETED") {
      drawGameOverMessage();
      requestAnimationFrame(mainLoop); // Continue to request animation frames to check for status changes
      return; // Skip the rest of the loop logic
    }
    
    lastUpdateTime = timestamp - (deltaTime % frameDuration); // Adjust for any overshoot of the frame duration
  }
  
// Log the ball's position
// console.log(`Ball position - X: ${game.ball.x.toFixed(2)}, Y: ${game.ball.y.toFixed(2)}`);

  requestAnimationFrame(mainLoop);
}

requestAnimationFrame(mainLoop); // Start the game loop

//----------------------DRAWING-----------------------------------------

function draw() {
  // Clear the canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw paddles using the updated positions
  drawPaddle(0, game.players.left.paddleY);
  drawPaddle(canvas.width - game.paddle.width, game.players.right.paddleY);

  // Draw the ball using the updated position
  drawBall(game.ball.x, game.ball.y);

  // Draw the white dash line in the middle
  drawWhiteDashLine();

  // Draw scores
  drawScores(); // Pass the data parameter to drawScores()
}

function drawPaddle(x, y) {
  ctx.fillStyle = "#fff";
  ctx.fillRect(x, y, game.paddle.width, game.paddle.height);
}

function drawBall(x, y) {
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

  // Calculate the position for scores in the top center
  var middleDashLineX = canvas.width / 2;
  var scoreTextWidth = ctx.measureText(game.players.left.score).width;
  var distanceFromDashLine = 30;

  // Set the height position in relation to the canvas height
  var heightPosition = canvas.height / 6;

  // Draw left player's score
  ctx.fillText(
    game.players.left.score,
    middleDashLineX - scoreTextWidth - distanceFromDashLine,
    heightPosition
  );

  // Draw right player's score
  ctx.fillText(
    game.players.right.score,
    middleDashLineX + distanceFromDashLine,
    heightPosition
  );
}

function drawGameOverMessage() {
  ctx.fillStyle = "#fff";
  ctx.font = '100px "Geo", sans-serif';

  var gameOverText = "Game Over!";
  var gameOverTextWidth = ctx.measureText(gameOverText).width;

  // Calculate the position for the game over message centered from the dash line
  var middleDashLineX = canvas.width / 2;
  var gameOverTextX = middleDashLineX - gameOverTextWidth / 2;

  // Set the height position at 2/3 of the canvas height
  var heightPosition = (2 / 3) * canvas.height;

  ctx.fillText(gameOverText, gameOverTextX, heightPosition);

  // Adjust font size for the player winning message
  ctx.font = '50px "Geo", sans-serif';

  // Calculate the position for the player winning message centered from the dash line
  var playerWinsText =
    "Player " +
    (game.players.left.score > game.players.right.score ? "Left" : "Right") +
    " Wins!";
  var playerWinsTextWidth = ctx.measureText(playerWinsText).width;
  var playerWinsTextX = middleDashLineX - playerWinsTextWidth / 2;

  ctx.fillText(playerWinsText, playerWinsTextX, heightPosition + 70); // Adjust vertical spacing
}

function drawPausedMessage() {
  ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas
  ctx.fillStyle = "rgba(0,0,0,0.75)"; // Semi-transparent overlay
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "#FFFFFF"; // White text
  ctx.font = "30px Arial";
  ctx.textAlign = "center";
  ctx.fillText("Game Paused", canvas.width / 2, canvas.height / 2);
}