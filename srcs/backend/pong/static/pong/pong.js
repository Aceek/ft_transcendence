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
    }

    function drawPaddle(x, y) {
        ctx.fillStyle = '#fff';
        ctx.fillRect(x, y, paddleWidth, paddleHeight);
    }

    function drawBall(x, y) {
        ctx.fillStyle = '#fff';
        ctx.fillRect(x - ballSize / 2, y - ballSize / 2, ballSize, ballSize);
    }

    // Start the game loop
    function update() {
        requestAnimationFrame(update);
    }

    update();
});
