/*TODO
    

*/
console.log('Pong.js is executed!');

const apiEndpoint = 'http://localhost:8000/api/pong/';
let gameId;  // Variable to store the game ID

function sendInitGameRequest() {
    fetch(apiEndpoint + 'init-game/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'player1_id': 1,  // Replace with your actual player 1 ID
            'player2_id': 2,  // Replace with your actual player 2 ID
        }),
    })
    .then(response => response.json())
    .then(gameState => {
        // Store the game ID
        gameId = gameState.game_id;

        // Handle the response if needed
        console.log(gameState);
    })
    .catch(error => console.error('Error:', error));
}

// Send init-game request when the DOM is loaded
sendInitGameRequest();

var canvas = document.getElementById('pongCanvas');
var ctx = canvas.getContext('2d');

// Paddle properties
var paddleWidth = 10;
var paddleHeight = 80;
// Local variable to track the paddle's Y position
let localPaddleY = (canvas.height - paddleHeight) / 2;
let opponentPaddleY = (canvas.height - paddleHeight) / 2;

// Function to update the local paddle position based on key presses
function updateLocalPaddlePosition(direction) {
    const speed = 10;

    // Update the local paddle position based on the direction
    localPaddleY += direction === 'ArrowUp' ? -speed : direction === 'ArrowDown' ? speed : 0;
}

// Event listeners for key presses
document.addEventListener('keydown', function (event) {
    console.log('Key pressed:', event.key);
    updateLocalPaddlePosition(event.key);
});

document.addEventListener('keyup', function (event) {
    console.log('Key released:', event.key);
    updateLocalPaddlePosition(''); // Reset direction on key release
});

// Throttle function to limit the rate of function invocation
function throttle(func, delay) {
    let lastCallTime = 0;

    return function (...args) {
        const now = new Date().getTime();

        if (now - lastCallTime >= delay) {
            func(...args);
            lastCallTime = now;
        }
    };
}

// Function to send the POST request to the server every 100ms
const sendPaddlePositionToServer = throttle(() => {
    // Make a POST request to the backend API for paddle movements
    fetch(apiEndpoint + `move-paddle/${gameId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'player_id': 1,
            'paddle_y': localPaddleY, // Send the local paddle position to the server
        }),
    })
    .then(response => response.json())
    .then(gameState => {
        // Handle the updated game state received from the backend
        updateGameView(gameState); // Pass the gameState as an argument
    })
    .catch(error => console.error('Error:', error));
}, 100);


// Function to fetch game info from the server every 100ms
const fetchGameInfoFromServer = throttle(() => {
    // Check if the 'gameId' is present
    if (gameId) {
        console.log('Fetching game info for game ID:', gameId);
        // Fetch paddle coordinates for the current game ID
        fetch(apiEndpoint + `game-info/${gameId}/`)
            .then(response => response.json())
            .then(gameInfo => {
                console.log('Received game info for game ID:', gameId);
                // Check if the 'paddle_coordinates' array is present in the response
                if (gameInfo.paddle_coordinates) {
                    // Update paddle positions based on server information
                    opponentPaddleY = findPaddleY(gameInfo.paddle_coordinates, 2);

                    // Print the Y positions of the paddles
                    console.log('Left Paddle Y:', localPaddleY);
                    console.log('Right Paddle Y:', opponentPaddleY);
                } else {
                    console.warn('No paddle coordinates found in game info response.');
                }
            })
            .catch(error => console.error('Error fetching game info:', error));
    } else {
        console.warn('No game ID.');
    }
}, 100);

// Helper function to find the paddle Y position for a specific player ID
function findPaddleY(paddleCoordinates, playerId) {
    const playerCoordinates = paddleCoordinates.find(pc => parseInt(pc.player_id) === playerId);
    return playerCoordinates ? playerCoordinates.paddle_y : 0; // Default to 0 if player not found
}

setInterval(sendPaddlePositionToServer, 100);
setInterval(fetchGameInfoFromServer, 100);


function draw() {
    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // // Draw paddles using the updated positions
    drawPaddle(0, localPaddleY);
    drawPaddle(canvas.width - paddleWidth, opponentPaddleY);

    // // Draw the ball using the updated position
    // drawBall(ballX, ballY);

    // Draw the white dash line in the middle
    drawWhiteDashLine();

    // Draw scores
    // drawScores(data);  // Pass the data parameter to drawScores()

    // // Check if the match is over and display a message
    // if (data.matchOver) {
    // 	drawGameOverMessage();
    // }
}

function drawPaddle(x, y) {
    ctx.fillStyle = '#fff';
    ctx.fillRect(x, y, paddleWidth, paddleHeight);
}

function drawBall(x, y) {
    ctx.fillStyle = '#fff';
    ctx.fillRect(x - ballSize / 2, y - ballSize / 2, ballSize, ballSize);
}

function drawWhiteDashLine() {
    ctx.strokeStyle = '#fff';
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(canvas.width / 2, 0);
    ctx.lineTo(canvas.width / 2, canvas.height);
    ctx.stroke();
    ctx.setLineDash([]);
}

function drawScores() {
    ctx.fillStyle = '#fff';
    ctx.font = '100px "Geo", sans-serif';

    // Calculate the position for scores in the top center
    var middleDashLineX = canvas.width / 2;
    var scoreTextWidth = ctx.measureText(leftPlayerScore).width;
    var distanceFromDashLine = 30;

    // Set the height position in relation to the canvas height
    var heightPosition = canvas.height / 6;

    // Draw left player's score
    ctx.fillText(leftPlayerScore, middleDashLineX - scoreTextWidth - distanceFromDashLine, heightPosition);

    // Draw right player's score
    ctx.fillText(rightPlayerScore, middleDashLineX + distanceFromDashLine, heightPosition);
}

function drawGameOverMessage() {
    ctx.fillStyle = '#fff';
    ctx.font = '100px "Geo", sans-serif';

    var gameOverText = 'Game Over!';
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
    var playerWinsText = 'Player ' + (leftPlayerScore > rightPlayerScore ? 'Left' : 'Right') + ' Wins!';
    var playerWinsTextWidth = ctx.measureText(playerWinsText).width;
    var playerWinsTextX = middleDashLineX - playerWinsTextWidth / 2;

    ctx.fillText(playerWinsText, playerWinsTextX, heightPosition + 70); // Adjust vertical spacing
}

// Function to update the game view based on the received game state
function updateGameView(data) {
    // Draw the updated state
    draw(data);
}

// Start the game loop
let lastTimestamp = 0;
function update(timestamp) {
    // Calculate the time elapsed since the last frame
    const elapsed = timestamp - lastTimestamp;

    // Control the frame rate (e.g., 120 frames per second)
    const frameRate = 1000 / 120; // 120 frames per second
    if (elapsed < frameRate) {
        requestAnimationFrame(update);
        return;
    }

    // Save the current timestamp for the next frame
    lastTimestamp = timestamp;

    // Continue the game loop
    requestAnimationFrame(update);
}

// Initial call to start the game loop
requestAnimationFrame(update);

update();
