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

// socket.onmessage = function (event) {
//   console.log("WebSocket message received:", event.data);
// };

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
    case "start_game":
      socket.send(JSON.stringify({ type: "start_game", message: "ready_to_play" }));
      break;
    default:
      console.log("Unknown message type:", data.type);
  }
};

socket.onclose = function (event) {
  console.log("WebSocket connection closed:", event);
};

//----------------------EVENT LISTENERS-----------------------------------------

// Global variables to track the last sent paddle positions
let lastSentPaddleY = null;

// Function to handle paddle movements and send updates to the server
function sendPaddlePositionUpdate() {
    // Check if there's a significant change in paddle positions
    if (game.players.left.paddleY !== lastSentPaddleY) {
        // Update last sent positions
        lastSentPaddleY = game.players.left.paddleY;

        // Send updated positions to the server
        socket.send(JSON.stringify({
            type: "paddle_position_update",
            PaddleY: game.players.left.paddleY,
        }));

        console.log("Paddle positions sent:", lastSentPaddleY);
    }
}

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
    // Determine the change in position
    let change = game.paddle.speed * (isPressed ? 1 : 0); // Adjust speed based on key state

    // Update paddle position based on the key pressed
    if (key === "ArrowUp") {
        game.players.left.paddleY -= change;
        sendPaddlePositionUpdate(); // Send position update
    } else if (key === "ArrowDown") {
        game.players.left.paddleY += change;
        sendPaddlePositionUpdate(); // Send position update
    }
}

//----------------------DATA INITALIZATION---------------------------------------

var game = {
  paddle: {
    width: 0,
    height: 0,
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
//   gameStatus: null,
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
//   console.log("Handling dynamic data:", dynamicData);
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

// // Main game loop
// function mainLoop() {
//   // Log the current game state for debugging
//   // console.log("Current game state:", JSON.stringify(game, null, 2));

//   draw();
//   requestAnimationFrame(mainLoop);
// }

// // Start the main game loop
// mainLoop();

let lastUpdateTime = 0;
const fps = 1000;
const frameDuration = 1000 / fps;

function interpolatePosition(lastPosition, speed, deltaTime) {
  // Calculate and return the new position based on the speed and the delta time
  return lastPosition + speed * (deltaTime / 1000); // Convert deltaTime from ms to seconds
}

function mainLoop(timestamp) {
  // Calculate the delta time since the last frame
  const deltaTime = timestamp - lastUpdateTime;
  
  if (deltaTime > frameDuration) {
    // Calculate the interpolated positions
    game.ball.x = interpolatePosition(game.ball.x, game.ball.speedX, deltaTime);
    game.ball.y = interpolatePosition(game.ball.y, game.ball.speedY, deltaTime);
    
    draw(); // Draw the frame with the interpolated positions
    
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

  // Check if the match is over and display a message
  if (game.gameStatus == "over") {
    drawGameOverMessage();
  }
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
    (game.players.left.score > game.players.left.right ? "Left" : "Right") +
    " Wins!";
  var playerWinsTextWidth = ctx.measureText(playerWinsText).width;
  var playerWinsTextX = middleDashLineX - playerWinsTextWidth / 2;

  ctx.fillText(playerWinsText, playerWinsTextX, heightPosition + 70); // Adjust vertical spacing
}
