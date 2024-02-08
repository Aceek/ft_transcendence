//----------------------TODO-----------------------------------------
//make the paddle mvt local
//interpolation for ball movement

//----------------------INITIALIZATION-----------------------------------------
    console.log('Pong.js is executed!');

// document.addEventListener('DOMContentLoaded', function () {
    var canvas = document.getElementById('pongCanvas');
    var ctx = canvas.getContext('2d');
    var socket = new WebSocket('ws://localhost:8000/ws/pong/');
    var currentState = null;
    var previousState = null;
    var interpolationRatio = 0.0;


//----------------------WEBSOCKET-----------------------------------------

    console.log('socket!');

    socket.onopen = function(event) {
        console.log('WebSocket connection opened:', event);
    };

    socket.onmessage = function(event) {
        console.log('WebSocket message received:', event.data);
        // Rest of the code...
    };

    socket.onmessage = function (event) {
        var data = JSON.parse(event.data);
    
        if (data.type === 'game.init') {
            initializeGame(data);
        } else if (data.type === 'game.update') {
            handleGameUpdate(data);
        }
    };

    socket.onclose = function(event) {
            console.log('WebSocket connection closed:', event);
    };
    
//----------------------KEYEVENT-----------------------------------------

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

//----------------------DATA INITALIZATION---------------------------------------

    var game = {
        paddle: {
            width: 0,
            height: 0
        },
        ball: {
            size: 0,
            x: 0,
            y: 0
        },
        players: {
            left: {
                paddleY: 0,
                score: 0
            },
            right: {
                paddleY: 0,
                score: 0
            }
        },
        matchOver: false,
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

        // Update game state
        updateGameState(data);
    }
    
    function updateGameState(data) {
        previousState = currentState;
        currentState = data;
    }

//----------------------GAME LOOP-----------------------------------------
    
    // Main game loop
    function mainLoop() {
        // updateInterpolationRatio();
        // updateGame();
        draw();
        requestAnimationFrame(mainLoop);
    }

    // Function to update interpolation ratio
    function updateInterpolationRatio() {
        if (previousState && currentState) {
            var currentTime = Date.now();
            var previousTime = previousState.timestamp;
            var currentStateTime = currentState.timestamp;
            interpolationRatio = (currentTime - previousTime) / (currentStateTime - previousTime);
        }
    }

    // Function to update the game state
    function updateGame() {
        if (currentState) {
            // Update the game state based on the current state
            // and interpolated values between the previous and current states
            // Example: Interpolate paddle positions, ball position, etc.
            
            // Interpolate paddle positions
            if (previousState) {
                console.log('Interpolating paddle positions...');
                console.log('Previous left paddle Y:', previousState.leftPaddleY);
                console.log('Current left paddle Y:', currentState.leftPaddleY);
                console.log('Previous right paddle Y:', previousState.rightPaddleY);
                console.log('Current right paddle Y:', currentState.rightPaddleY);
    
                game.players.left.paddleY = interpolate(previousState.leftPaddleY, currentState.leftPaddleY);
                game.players.right.paddleY = interpolate(previousState.rightPaddleY, currentState.rightPaddleY);
    
                // Interpolate ball position
                console.log('Interpolating ball position...');
                console.log('Previous ball X:', previousState.ball.x);
                console.log('Current ball X:', currentState.ball.x);
                console.log('Previous ball Y:', previousState.ball.y);
                console.log('Current ball Y:', currentState.ball.y);
    
                game.ball.x = interpolate(previousState.ball.x, currentState.ball.x);
                game.ball.y = interpolate(previousState.ball.y, currentState.ball.y);
            } else {
                // Set initial paddle positions
                console.log('Setting initial positions...');
                console.log('Current left paddle Y:', currentState.leftPaddleY);
                console.log('Current right paddle Y:', currentState.rightPaddleY);
    
                game.players.left.paddleY = currentState.leftPaddleY;
                game.players.right.paddleY = currentState.rightPaddleY;
    
                // Set initial ball position
                console.log('Setting initial ball position...');
                console.log('Current ball X:', currentState.ball.x);
                console.log('Current ball Y:', currentState.ball.y);
    
                game.ball.x = currentState.ball.x;
                game.ball.y = currentState.ball.y;
            }
        }
    }

    function interpolate(prevValue, curValue) {
        return prevValue + (curValue - prevValue) * interpolationRatio;
    }

    // Start the main game loop
    mainLoop();

//----------------------DRAWING-----------------------------------------

	function draw() {
		// Clear the canvas
		ctx.clearRect(0, 0, canvas.width, canvas.height);
	
		// Draw paddles using the updated positions
		drawPaddle(0,  game.players.left.paddleY);
		drawPaddle(canvas.width - game.paddle.width,  game.players.right.paddleY);
	
		// Draw the ball using the updated position
		drawBall(game.ball.x, game.ball.y);
	
		// Draw the white dash line in the middle
		drawWhiteDashLine();
	
		// Draw scores
		drawScores();  // Pass the data parameter to drawScores()
	
		// Check if the match is over and display a message
		if (game.matchOver) {
			drawGameOverMessage();
		}
	}

    function drawPaddle(x, y) {
        ctx.fillStyle = '#fff';
        ctx.fillRect(x, y, game.paddle.width, game.paddle.height);
    }

    function drawBall(x, y) {
        ctx.fillStyle = '#fff';
        ctx.fillRect(x - game.ball.size / 2, y - game.ball.size / 2, game.ball.size, game.ball.size);
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
        var scoreTextWidth = ctx.measureText(game.players.left.score).width;
        var distanceFromDashLine = 30;

        // Set the height position in relation to the canvas height
        var heightPosition = canvas.height / 6;

        // Draw left player's score
        ctx.fillText(game.players.left.score, middleDashLineX - scoreTextWidth - distanceFromDashLine, heightPosition);

        // Draw right player's score
        ctx.fillText(game.players.right.score, middleDashLineX + distanceFromDashLine, heightPosition);
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
		var playerWinsText = 'Player ' + (game.players.left.score > game.players.left.right ? 'Left' : 'Right') + ' Wins!';
		var playerWinsTextWidth = ctx.measureText(playerWinsText).width;
		var playerWinsTextX = middleDashLineX - playerWinsTextWidth / 2;
	
		ctx.fillText(playerWinsText, playerWinsTextX, heightPosition + 70); // Adjust vertical spacing
	}
// });