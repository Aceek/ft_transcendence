console.log('Pong.js is executed!');

document.addEventListener('DOMContentLoaded', function () {
    var canvas = document.getElementById('pongCanvas');
    var ctx = canvas.getContext('2d');
    var socket = new WebSocket('ws://' + window.location.host + '/ws/pong/');

    socket.onopen = function(event) {
        console.log('WebSocket connection opened:', event);
    };
    
    socket.onmessage = function(event) {
        console.log('WebSocket message received:', event.data);
        // Rest of the code...
    };
    
    socket.onclose = function(event) {
        console.log('WebSocket connection closed:', event);
    };

    // Paddle properties
    var paddleWidth = 10;
    var paddleHeight = 80;
    var leftPaddleY = (canvas.height - paddleHeight) / 2;
    var rightPaddleY = (canvas.height - paddleHeight) / 2;

    // Ball properties
    var ballSize = 10;
    var ballX = canvas.width / 2;
    var ballY = canvas.height / 2;

    // Scores
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
        // Send WebSocket message for paddle movements
        socket.send(JSON.stringify({
            'message': 'paddle_movement',
            'key': key,
            'isPressed': isPressed,
        }));
    }

    socket.onmessage = function (event) {
        var data = JSON.parse(event.data);

        if (data.type === 'game.update') {
            handleGameUpdate(data);
        }
    };

	function handleGameUpdate(data) {
		// Update paddle positions based on server information
		leftPaddleY = data.leftPaddleY;
		rightPaddleY = data.rightPaddleY;
	
		// Update ball position based on server information
		ballX = data.ballPosition.x;
		ballY = data.ballPosition.y;
	
		// Update scores
		leftPlayerScore = data.leftPlayerScore;
		rightPlayerScore = data.rightPlayerScore;
	
		// Log the value of matchOver
		console.log('Match Over:', data.matchOver);
	
		// Draw the updated state
		draw(data);  // Pass the data parameter to draw()
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
