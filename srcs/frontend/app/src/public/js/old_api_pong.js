/*TODO
    

*/
console.log('Pong.js is executed!');

const apiEndpoint = 'http://localhost:8000/api/pong/';
var canvas = document.getElementById('pongCanvas');
var ctx = canvas.getContext('2d');
let gameId;
let screen = {};
let players = [];
let ball = {};
let paddle = {};

function sendInitGameRequest() {
    return fetch(apiEndpoint + 'init-game/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'player1_id': 1,
            'player2_id': 2,
        }),
    })
    .then(response => response.json())
    .then(game => {
        gameId = game.id;
        screen = game.screen;
        players = game.players;
        ball = game.ball;
        paddle = game.paddle;

        console.log(game);

        startGame(gameId);
        // Start the game loop after initializing the game
        setTimeout(() => {
            // Start the game loop after initializing the game
            startGameLoop();
        }, 1000); // Adjust the delay time in milliseconds (e.g., 1000 for 1 second)
    })
    .catch(error => console.error('Error:', error));
}


let updateInterval = 100; // Adjust the interval based on your preferences
let lastUpdate = 0;
let lastTimestamp = 0;
let interpolationDuration = 16;

function startGameLoop() {
    function update(timestamp) {
        // Calculate the time elapsed since the last update
        const deltaTime = timestamp - lastTimestamp;
        lastTimestamp = timestamp;
        
        // Clear the canvas
        ctx.clearRect(0, 0, screen.width, screen.height);

        // Draw the game content
        draw();

        // Calculate the target position of the ball
        const targetX = ball.x + ball.speed_x * (deltaTime / 1000); // Convert deltaTime to seconds
        const targetY = ball.y + ball.speed_y * (deltaTime / 1000); // Convert deltaTime to seconds

        // Interpolate between current and target positions
        const interpolatedX = interpolate(ball.x, targetX, deltaTime, interpolationDuration);
        const interpolatedY = interpolate(ball.y, targetY, deltaTime, interpolationDuration);

        // Update ball position
        ball.x = interpolatedX;
        ball.y = interpolatedY;

        // Update paddle position based on arrow keys
        if (keys.ArrowUp && players[0].paddle_y > 0) {
            players[0].paddle_y -= paddle.speed; // Adjust the value based on desired speed
            sendPaddleCoordinates();
        }
        if (keys.ArrowDown && players[0].paddle_y < screen.height - paddle.height) {
            players[0].paddle_y += paddle.speed; // Adjust the value based on desired speed
            sendPaddleCoordinates();
        }

        // Send paddle coordinates to API at regular intervals
        if (timestamp - lastUpdate > updateInterval) {
            getGameData();
            lastUpdate = timestamp;
        }

        // Continue the game loop
        requestAnimationFrame(update);
    }

    // Initial call to start the game loop
    let lastTimestamp = performance.now(); // Initialize lastTimestamp
    requestAnimationFrame(update);
}

function interpolate(start, end, elapsedTime, duration) {
    // Linear interpolation function
    return start + (end - start) * (elapsedTime / duration);
}

function sendPaddleCoordinates() {
    // Send a single request with updated paddle coordinates
    fetch(apiEndpoint + 'update-paddle/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'game_id': gameId,
            'player_id': 1, // Assuming player 1 for now
            'paddle_y': players[0].paddle_y,
        }),
    })
    .then(response => response.json())
    .then(updatedGame => {
        // Handle any response if needed
    })
    .catch(error => console.error('Error updating paddle:', error));
}

function getGameData() {
    fetch(apiEndpoint + 'update-game-data/' + gameId + '/')
        .then(response => response.json())
        .then(gameData => {
            // Update game state with received data
            // players[0].paddle_y = gameData.p1_y;
            players[1].paddle_y = gameData.p2_y;
            ball.x = gameData.b_x;
            ball.y = gameData.b_y;

            // Print received game data for debugging
            console.log('Received Game Data:', gameData);
        })
        .catch(error => console.error('Error getting game data:', error));
}

function startGame(gameId) {
    // Call the API endpoint to start the game
    fetch(apiEndpoint + 'start-game/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'game_id': gameId,
        }),
    })
    .then(response => response.json())
    .catch(error => {
        console.error('Error starting the game:', error);
    });
}

function draw() {
    // Draw paddles using the updated positions
    drawPaddle(0, players[0].paddle_y);
    drawPaddle(screen.width - paddle.width, players[1].paddle_y);

    // Draw the ball using the updated position
    drawBall(ball.x, ball.y);

    // Draw the white dash line in the middle
    drawWhiteDashLine();

    // Draw scores
    drawScores();

    // // Check if the match is over and display a message
    // if (data.matchOver) {
    // 	drawGameOverMessage();
    // }
}

function drawPaddle(x, y) {
    ctx.fillStyle = '#fff';
    ctx.fillRect(x, y, paddle.width, paddle.height);
}

function drawBall(x, y) {
    ctx.fillStyle = '#fff';
    ctx.fillRect(x - ball.width / 2, y - ball.height / 2, ball.width, ball.height);
}

function drawWhiteDashLine() {
    ctx.strokeStyle = '#fff';
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(screen.width / 2, 0);
    ctx.lineTo(screen.width / 2, screen.height);
    ctx.stroke();
    ctx.setLineDash([]);
}

function drawScores() {
    ctx.fillStyle = '#fff';
    ctx.font = '100px "Geo", sans-serif';

    // Calculate the position for scores in the top center
    var middleDashLineX = screen.width / 2;
    var scoreTextWidth = ctx.measureText(players[0].score).width;
    var distanceFromDashLine = 30;

    // Set the height position in relation to the canvas height
    var heightPosition = screen.height / 6;

    // Draw left player's score
    ctx.fillText(players[0].score, middleDashLineX - scoreTextWidth - distanceFromDashLine, heightPosition);

    // Draw right player's score
    ctx.fillText(players[1].score, middleDashLineX + distanceFromDashLine, heightPosition);
}

// Send init-game request when the DOM is loaded
sendInitGameRequest();


/*---------------------------------------------------------------------------------*/

document.addEventListener('keydown', handleKeyDown);
document.addEventListener('keyup', handleKeyUp);

let keys = {
    ArrowUp: false,
    ArrowDown: false,
};

function handleKeyDown(event) {
    keys[event.key] = true;
}

function handleKeyUp(event) {
    keys[event.key] = false;
}