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

        // Start the game loop after initializing the game
        startGameLoop();
    })
    .catch(error => console.error('Error:', error));
}


let updateInterval = 200; // Adjust the interval based on your preferences
let lastUpdate = 0;

function startGameLoop() {
    function update(timestamp) {
        // Clear the canvas
        ctx.clearRect(0, 0, screen.width, screen.height);

        // Draw the game content
        draw();

        // Update paddle position based on arrow keys
        if (keys.ArrowUp && players[0].paddle_y > 0) {
            players[0].paddle_y -= paddle.speed; // Adjust the value based on desired speed
        }
        if (keys.ArrowDown && players[0].paddle_y < screen.height - paddle.height) {
            players[0].paddle_y += paddle.speed; // Adjust the value based on desired speed
        }

        // Send paddle coordinates to API at regular intervals
        if (timestamp - lastUpdate > updateInterval) {
            sendPaddleCoordinates();
            lastUpdate = timestamp;
        }

        // Continue the game loop
        requestAnimationFrame(update);
    }

    // Initial call to start the game loop
    requestAnimationFrame(update);
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
