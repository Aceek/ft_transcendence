// pong.js

document.addEventListener('DOMContentLoaded', function () {
    var canvas = document.getElementById('pongCanvas');
    var ctx = canvas.getContext('2d');

    // Paddle properties
    var paddleWidth = 10;
    var paddleHeight = 80;
    var leftPaddleY = (canvas.height - paddleHeight) / 2;
    var rightPaddleY = (canvas.height - paddleHeight) / 2;

    // Ball properties
    var ballSize = 10;
    var ballX = canvas.width / 2;
    var ballY = canvas.height / 2;
    var ballSpeedX = 5;
    var ballSpeedY = 5;

    // Keyboard controls
    var leftPlayerUpPressed = false;
    var leftPlayerDownPressed = false;
    var rightPlayerUpPressed = false;
    var rightPlayerDownPressed = false;

    // Scores
	var limitScore = 10;
    var leftPlayerScore = 0;
    var rightPlayerScore = 0;

    // Event listeners for key presses
    document.addEventListener('keydown', function (event) {
        handleKeyPress(event.key, true);
    });

    document.addEventListener('keyup', function (event) {
        handleKeyPress(event.key, false);
    });

    function handleKeyPress(key, isPressed) {
        // Left player controls (W and S)
        if (key === 'w') {
            leftPlayerUpPressed = isPressed;
        } else if (key === 's') {
            leftPlayerDownPressed = isPressed;
        }

        // Right player controls (Arrow Up and Arrow Down)
        if (key === 'ArrowUp') {
            rightPlayerUpPressed = isPressed;
        } else if (key === 'ArrowDown') {
            rightPlayerDownPressed = isPressed;
        }
    }

    function draw() {
        // Clear the canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw the dashed line in the middle
        drawDashedLine();

        // Update paddle positions based on key presses
        updatePaddlePositions();

        // Draw paddles
        drawPaddle(0, leftPaddleY);
        drawPaddle(canvas.width - paddleWidth, rightPaddleY);

        // Update ball position and check for collisions
        updateBall();

        // Draw the ball
        drawBall(ballX, ballY);

        // Draw the score bar
        drawScoreBar();
    }

    function drawDashedLine() {
        ctx.strokeStyle = '#fff';
        ctx.setLineDash([5, 15]); // 5-pixel dashes, 15-pixel gaps
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(canvas.width / 2, 0);
        ctx.lineTo(canvas.width / 2, canvas.height);
        ctx.stroke();
        ctx.setLineDash([]); // Reset line dash
    }

    function updatePaddlePositions() {
        // Update left player paddle position
        if (leftPlayerUpPressed && leftPaddleY > 0) {
            leftPaddleY -= 5;
        } else if (leftPlayerDownPressed && leftPaddleY + paddleHeight < canvas.height) {
            leftPaddleY += 5;
        }

        // Update right player paddle position
        if (rightPlayerUpPressed && rightPaddleY > 0) {
            rightPaddleY -= 5;
        } else if (rightPlayerDownPressed && rightPaddleY + paddleHeight < canvas.height) {
            rightPaddleY += 5;
        }
    }

    function updateBall() {
		// Check if the game is over
		if (leftPlayerScore >= limitScore || rightPlayerScore >= limitScore) {
			return; // Don't update the ball's position if the game is over
		}

        // Move the ball
        ballX += ballSpeedX;
        ballY += ballSpeedY;

        // Check for collisions with paddles
        handlePaddleCollisions();

        // Check for scoring
        handleScoring();

        // Bounce off the top and bottom edges
        handleWallCollisions();
    }

    function handlePaddleCollisions() {
        // Check for collision with left paddle
        if (ballX - ballSize < paddleWidth && isCollidingWithPaddle(leftPaddleY)) {
            handleCollision(leftPaddleY);
        }

        // Check for collision with right paddle
        if (ballX + ballSize > canvas.width - paddleWidth && isCollidingWithPaddle(rightPaddleY)) {
            handleCollision(rightPaddleY);
        }
    }

    function isCollidingWithPaddle(paddleY) {
        return ballY > paddleY && ballY < paddleY + paddleHeight;
    }

    function handleCollision(paddleY) {
        // Ball collided with a paddle, reverse its x-direction
        ballSpeedX = -ballSpeedX;

        // Adjust ball's trajectory based on where it hit the paddle
        var deltaY = ballY - (paddleY + paddleHeight / 2);
        ballSpeedY = deltaY * 0.1; // Adjust the multiplier as needed for different bounce angles
    }

    function handleScoring() {
        // Check if the ball went past the left paddle
        if (ballX < 0) {
            // Right player scores a point
            rightPlayerScore++;
            resetBall();
        }

        // Check if the ball went past the right paddle
        if (ballX > canvas.width) {
            // Left player scores a point
            leftPlayerScore++;
            resetBall();
        }
    }

	function resetBall() {
		// Reset the ball position to the center
		ballX = canvas.width / 2;
		ballY = canvas.height / 2;
	
		// Reset ball speed based on which player scored
		if (leftPlayerScore === 0 && rightPlayerScore === 0) {
			// First game, launch the ball in a random direction
			var randomDirection = Math.random() > 0.5 ? 1 : -1; // Randomly choose between 1 and -1
			ballSpeedX = randomDirection * Math.abs(ballSpeedX);
		} else {
			// Subsequent games, switch directions
			ballSpeedX = -ballSpeedX;
		}
	
		ballSpeedY = Math.abs(ballSpeedY); // Reset the ball's vertical speed
	}

    function handleWallCollisions() {
        // Bounce off the top and bottom edges
        if (ballY + ballSize > canvas.height || ballY - ballSize < 0) {
            ballSpeedY = -ballSpeedY;
        }
    }

    function drawPaddle(x, y) {
        ctx.fillStyle = '#fff';
        ctx.fillRect(x, y, paddleWidth, paddleHeight);
    }

    function drawBall(x, y) {
        ctx.fillStyle = '#fff';
        ctx.beginPath();
        ctx.arc(x, y, ballSize, 0, Math.PI * 2);
        ctx.fill();
        ctx.closePath();
    }

	function drawScoreBar() {
		// Use the "Geo" font
		ctx.font = '100px "Geo", sans-serif'; // Adjust the font size as needed
	
		// Calculate the x positions for each player's score
		var leftXPosition = canvas.width / 4 - ctx.measureText(leftPlayerScore).width / 2;
		var rightXPosition = (3 * canvas.width) / 4 - ctx.measureText(rightPlayerScore).width / 2;
		
		var yPosition = canvas.height / 6;
	
		// Draw the score numbers
		ctx.fillStyle = '#fff';
		ctx.fillText(leftPlayerScore, leftXPosition, yPosition);
		ctx.fillText(rightPlayerScore, rightXPosition, yPosition);
	}
	
    function checkScore() {
        // Check if either player has reached the limit score
        if (leftPlayerScore >= limitScore || rightPlayerScore >= limitScore) {
            // Display the winning message
            var winnerMessage = leftPlayerScore >= limitScore ? "Player 1 Wins!" : "Player 2 Wins!";
            var winnerXPosition = canvas.width / 2 - ctx.measureText(winnerMessage).width / 2;
            var winnerYPosition = canvas.height * 3 / 4;

            ctx.font = '100px "Geo", sans-serif'; // Adjust the font size for the winning message
            ctx.fillText(winnerMessage, winnerXPosition, winnerYPosition);

            // Reset the game after a short delay
            setTimeout(resetGame, 3000);
        }
    }

	function resetGame() {
        leftPlayerScore = 0;
        rightPlayerScore = 0;
        resetBall();
    }

    function update() {
        // Move paddles, update ball position, etc.

        // Call the updated ball function
        updateBall();

        // Draw the updated state
        draw();

        // Check the score
        checkScore();
		
        requestAnimationFrame(update);
    }

    // Start the game loop
    update();
});
