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
  console.log("WebSocket message received:", event.data);
};

socket.onmessage = function (event) {
  var data = JSON.parse(event.data);
  // console.log("WebSocket message received:", data);

  if (data.type === "game.init") {
    initializeGame(data);
    console.log(data.localIP);
  } else if (data.type === "game.update") {
    handleGameUpdate(data);
  } else if (data.type === "start_game") {
    socket.send(
      JSON.stringify({ type: "start_game", message: "ready_to_play" })
    );
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
  matchOver: false,
  localIP: 0,
};

function initializeGame(data) {
  // Initialize the game state using the received data
  game.paddle.width = data.paddleWidth;
  game.paddle.height = data.paddleHeight;
  game.ball.size = data.ballSize;
  game.players.left.paddleY = data.initialLeftPaddleY;
  game.players.right.paddleY = data.initialRightPaddleY;
  game.ball.x = data.initialBallPosition.x;
  game.ball.y = data.initialBallPosition.y;
  game.players.left.score = data.initialLeftPlayerScore;
  game.players.right.score = data.initialRightPlayerScore;
  game.matchOver = data.matchOver;
  game.localIP = data.localIP;
}

//----------------------GAME UPDATE-----------------------------------------

function handleGameUpdate(data) {
  // Update paddle positions based on server information
  game.players.left.paddleY = data.leftPaddleY;
  game.players.right.paddleY = data.rightPaddleY;

  // Update ball position based on server information
  game.ball.x = data.ball.x;
  game.ball.y = data.ball.y;

  // Update scores
  game.players.left.score = data.leftPlayerScore;
  game.players.right.score = data.rightPlayerScore;
}

//----------------------GAME LOOP-----------------------------------------

// Main game loop
function mainLoop() {
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
  if (game.matchOver) {
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
