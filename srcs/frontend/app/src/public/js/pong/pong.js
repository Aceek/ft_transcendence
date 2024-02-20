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
  console.log("WebSocket message received:", data);

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

let leftPaddleState = {
  up: false,
  down: false,
};

let rightPaddleState = {
  up: false,
  down: false,
};

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
  // Update the corresponding paddle state based on the pressed key
  if (key === "w") {
    leftPaddleState.up = isPressed;
  } else if (key === "s") {
    leftPaddleState.down = isPressed;
  } else if (key === "ArrowUp") {
    rightPaddleState.up = isPressed;
  } else if (key === "ArrowDown") {
    rightPaddleState.down = isPressed;
  }

  // Send WebSocket messages for paddle movements
  console.log("Sending paddle movements:", leftPaddleState, rightPaddleState);
  socket.send(
    JSON.stringify({
      message: "paddle_movement",
      leftPaddleState: leftPaddleState,
      rightPaddleState: rightPaddleState,
    })
  );
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
  gameStatus: null,
  userID: null,
};

function handleStaticData(staticData) {
  console.log("Received static data:", staticData);

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
  console.log("Static game settings parsed and updated:", game);
}

function handleDynamicData(dynamicData) {
  console.log("Handling dynamic data:", dynamicData);

  // Parse the JSON strings in the dynamic data
  const ballData = JSON.parse(dynamicData.ball);
  const leftPaddleData = JSON.parse(dynamicData.lp);
  const rightPaddleData = JSON.parse(dynamicData.rp);

  // Update the game state with parsed dynamic data
  game.ball.x = ballData.x;
  game.ball.y = ballData.y;
  game.ball.speedX = ballData.speedX; // Assuming you want to use speedX and speedY
  game.ball.speedY = ballData.speedY;
  game.players.left.paddleY = leftPaddleData.y;
  game.players.right.paddleY = rightPaddleData.y;
  game.players.left.score = parseInt(dynamicData.ls, 10);
  game.players.right.score = parseInt(dynamicData.rs, 10);
  game.gameStatus = parseInt(dynamicData.gs, 10); // Assuming gs is the game status

  // Log the updated game state for debugging
  console.log("Updated game state with dynamic data:", game);
}

// function initializeGame(data) {
//   // Initialize the game state using the received data
//   game.paddle.width = data.paddleWidth;
//   game.paddle.height = data.paddleHeight;
//   game.ball.size = data.ballSize;
//   game.players.left.paddleY = data.initialLeftPaddleY;
//   game.players.right.paddleY = data.initialRightPaddleY;
//   game.ball.x = data.initialBallPosition.x;
//   game.ball.y = data.initialBallPosition.y;
//   game.players.left.score = data.initialLeftPlayerScore;
//   game.players.right.score = data.initialRightPlayerScore;
//   game.gameStatus = data.gameStatus;
// }

//----------------------GAME UPDATE-----------------------------------------

// function handleGameUpdate(data) {
//   // Update paddle positions based on server information
//   game.players.left.paddleY = data.leftPaddleY;
//   game.players.right.paddleY = data.rightPaddleY;

//   // Update ball position based on server information
//   game.ball.x = data.ball.x;
//   game.ball.y = data.ball.y;

//   // Update scores
//   game.players.left.score = data.leftPlayerScore;
//   game.players.right.score = data.rightPlayerScore;
// }

// function handleGameState(gameState) {
//   // console.log("Handling game state:", gameState);
  
//   // Deserialize the 'ball' field if it was serialized as a string
//   if (typeof gameState.ball === "string") {
//     gameState.ball = JSON.parse(gameState.ball);
//   }

//   // Update the game state with the received data
//   game.players.left.score = parseInt(gameState.lpS, 10);
//   game.players.left.paddleY = parseInt(gameState.lpY, 10);
//   game.players.right.score = parseInt(gameState.rpS, 10);
//   game.players.right.paddleY = parseInt(gameState.rpY, 10);
//   game.ball.x = gameState.ball.x;
//   game.ball.y = gameState.ball.y;
//   game.gameStatus = gameState.gS;
//   game.userID = gameState.user_id;

  // Log the updated game state for debugging
  // console.log("Updated game state:", game);


//----------------------GAME LOOP-----------------------------------------

// Main game loop
function mainLoop() {
  // Log the current game state for debugging
  console.log("Current game state:", JSON.stringify(game, null, 2));

  draw();
  requestAnimationFrame(mainLoop);
}

// Start the main game loop
mainLoop();

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
