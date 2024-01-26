console.log('Pong.js is executed!');

document.addEventListener('DOMContentLoaded', function () {
    var canvas = document.getElementById('pongCanvas');
    var ctx = canvas.getContext('2d');

    // Replace WebSocket with API endpoint
    const apiEndpoint = 'http://localhost:8000/api/move-paddle/';

    // Paddle properties
    var paddleWidth = 10;
    var paddleHeight = 80;
    var leftPaddleY = (canvas.height - paddleHeight) / 2;
    var rightPaddleY = (canvas.height - paddleHeight) / 2;

    // Event listeners for key presses
    document.addEventListener('keydown', function (event) {
        handleKeyPress(event.key, true);
    });

    document.addEventListener('keyup', function (event) {
        handleKeyPress(event.key, false);
    });

    function handleKeyPress(key, isPressed) {
        // Make a POST request to the backend API for paddle movements
        fetch(apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'game_id': 1,  // Replace with your actual game ID
                'paddle_left_y': leftPaddleY,  // Send the current position of the left paddle
                'paddle_right_y': rightPaddleY,  // Send the current position of the right paddle
                'key': key,
                'isPressed': isPressed,
            }),
        })
        .then(response => response.json())
        .then(gameState => {
            // Handle the updated game state received from the backend
            updateGameView(gameState);
        })
        .catch(error => console.error('Error:', error));
    }

    // Function to update the game view based on the received game state
    function updateGameView(data) {
        // Update paddle positions based on server information
        leftPaddleY = data.leftPaddleY;
        rightPaddleY = data.rightPaddleY;

        // Draw the updated state
        draw(data);
    }
	
	function draw(data) {
		// Clear the canvas
		ctx.clearRect(0, 0, canvas.width, canvas.height);
	
		// Draw paddles using the updated positions
		drawPaddle(0, leftPaddleY);
		drawPaddle(canvas.width - paddleWidth, rightPaddleY);
	
		// Draw the ball using the updated position
		drawBall(ballX, ballY);
	
		// Draw the white dash line in the middle
		drawWhiteDashLine();
	
		// Draw scores
		drawScores(data);  // Pass the data parameter to drawScores()
	
		// Check if the match is over and display a message
		if (data.matchOver) {
			drawGameOverMessage();
		}
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

    // Start the game loop
    function update() {
        requestAnimationFrame(update);
    }

    update();
});
