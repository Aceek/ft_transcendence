export class GameRenderer {
    constructor(ctx, game) {
        this.ctx = ctx;
        this.game = game;
    }

    draw() {
        const { ctx, game } = this;

        if (game.status === -1) {
            return;
        }
        
        ctx.clearRect(0, 0, game.canvasWidth, game.canvasHeight);
        
        game.players.forEach(player => {
            // Uncomment the following line if you need to check the calculated 'x' value for any reason
            // const x = player.side === 'left' ? game.paddleBorderDistance : game.canvasWidth - player.paddleWidth - game.paddleBorderDistance;
        
            // Print player paddle properties for debugging or monitoring
            console.log(`Player [${player.id}] Paddle Position and Size: X=${player.paddleX}, Y=${player.paddleY}, Width=${player.paddleWidth}, Height=${player.paddleHeight}`);
        
            this.drawPaddle(player.paddleX, player.paddleY, player.paddleWidth, player.paddleHeight);
        });
        
        
        this.drawBall(game.ball.x, game.ball.y);
        
        this.drawWhiteDashLine();

        this.drawScores();
        
        if (game.countdown !== null && game.countdown > 0) {
            this.drawTwoPartMessage(game.countdown.toString(),
                "Get ready...")
        }

        if (game.status === 0 && (game.countdown === null || game.countdown === 0)) {
            this.drawTwoPartMessage("Room joined!", 
                "Waiting for other players to start...");
        }

        if (game.status === 2 && (game.countdown === null || game.countdown === 0)) {
            this.drawTwoPartMessage("Game Paused!",
                "Waiting for other players to resume...");
        }

        if (game.status === 3 && (game.countdown === null || game.countdown === 0)) {
            this.drawTwoPartMessage("Game Over!",
                "Press Enter to restart...")
        }
    }

    drawPaddle(x, y, paddleWidth, paddleHeight) {
        this.ctx.fillStyle = "#fff";
        this.ctx.fillRect(x, y, paddleWidth, paddleHeight);
    }

    drawBall(x, y) {
        this.ctx.fillStyle = "#fff";
        this.ctx.fillRect(x - this.game.ball.size / 2, y - this.game.ball.size / 2, this.game.ball.size, this.game.ball.size);
    }

    drawWhiteDashLine() {
        this.ctx.strokeStyle = "#fff";
        this.ctx.setLineDash([5, 5]);
        this.ctx.beginPath();
        this.ctx.moveTo(this.game.canvasWidth / 2, 0);
        this.ctx.lineTo(this.game.canvasWidth / 2, this.game.canvasHeight);
        this.ctx.stroke();
        this.ctx.setLineDash([]);
    }

    drawScores() {
        this.ctx.fillStyle = "#fff";
        this.ctx.font = '100px "Geo", sans-serif';
        const distanceFromCenter = this.game.canvasHeight / 5;
        const distanceFromTop = this.game.canvasHeight / 4;
    
        this.game.players.forEach((player) => {
            let x;
            if (player.side === 'left') {
                // Align the left player's score to the left of the center line
                x = (this.game.canvasWidth / 2) - distanceFromCenter;
            } else {
                // Align the right player's score to the right of the center line
                x = (this.game.canvasWidth / 2) + distanceFromCenter;
            }
    
            // Use the fixed distance from the top for Y
            const textHeight = this.ctx.measureText(player.score).height
            const y = distanceFromTop;
    
            this.ctx.fillText(player.score, x, y);
        });
    }

    drawTwoPartMessage(mainText, subText) {
        this.ctx.fillStyle = "#fff";
        this.ctx.textAlign = "center";
    
        // Fonts setup
        const mainFont = '70px "Geo", sans-serif'; // Font for the main message
        const subFont = '25px "Geo", sans-serif'; // Font for the sub-message
        const gapBetweenMessages = 50; // Space between the two messages
    
        // Measure main text height
        this.ctx.font = mainFont;
        const mainTextMetrics = this.ctx.measureText(mainText);
        const mainTextHeight = mainTextMetrics.actualBoundingBoxAscent + mainTextMetrics.actualBoundingBoxDescent;
    
        // Measure sub text height
        this.ctx.font = subFont;
        const subTextMetrics = this.ctx.measureText(subText);
        const subTextHeight = subTextMetrics.actualBoundingBoxAscent + subTextMetrics.actualBoundingBoxDescent;
    
        // Calculate total height and adjust starting Y position for 2/3 down the canvas
        const startY = (this.game.canvasHeight * 3 / 4) - (mainTextHeight + subTextHeight + gapBetweenMessages) / 2 + mainTextHeight;
    
        // Draw main message
        this.ctx.font = mainFont;
        this.ctx.fillText(mainText, this.game.canvasWidth / 2, startY);
    
        // Draw sub-message
        this.ctx.font = subFont;
        this.ctx.fillText(subText, this.game.canvasWidth / 2, startY + gapBetweenMessages);
    }
}

