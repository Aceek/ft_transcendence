document.addEventListener('DOMContentLoaded', function () {
    var canvas = document.getElementById('pongCanvas');
    var ctx = canvas.getContext('2d');
    var socket = new WebSocket('ws://' + window.location.host + '/ws/pong/');

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

        // Draw the updated state
        draw();
    }

    function draw() {
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
        drawScores();

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
        ctx.fillText('Game Over!', canvas.width / 2 - 300, canvas.height / 2 - 100);
        ctx.font = '50px "Geo", sans-serif';
        ctx.fillText('Player ' + (leftPlayerScore > rightPlayerScore ? 'Left' : 'Right') + ' Wins!', canvas.width / 2 - 250, canvas.height / 2);
    }

    // Start the game loop
    function update() {
        requestAnimationFrame(update);
    }

    update();
});
