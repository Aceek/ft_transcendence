export class GameRenderer {
    constructor(ctx, game) {
        this.ctx = ctx;
        this.game = game;
    }

    draw() {

        this.ctx.clearRect(0, 0, this.game.canvasWidth, this.game.canvasHeight);
        this.drawWhiteDashLine();
        
        if (this.game.status !== -1) {
            this.drawScores();
            this.drawBall(this.game.ball.x, this.game.ball.y);
            this.game.players.forEach(player => {
                this.drawPaddle(player);
            });
        }
        
        if (this.game.countdown !== null && this.game.countdown > 0) {
            if (this.game.type === 'tournament' && this.game.status === 2) {
                this.drawTwoPartMessage(this.game.countdown.toString(),
                "Opponent forfeiting in...");
            } else {
                this.drawTwoPartMessage(this.game.countdown.toString(),
                "Get ready...");
            }
        } else if (this.game.status === 2) {
            if (!(this.game.type === 'tournament' && this.game.countdown === 0)) {
                this.drawTwoPartMessage("Game Paused!",
                    "Waiting for other players to resume...");
            }
        } else if (this.game.status === -1) {
            this.drawTwoPartMessage("Room joined!", 
                "Waiting for other players to start...");
        } else if (this.game.status === 3) {
            if (this.game.type === 'tournament') {
                this.drawTwoPartMessage("Game Over!",
                    "Press Enter to go back to tournament page...");
            } else if (this.game.type === "standard") {
                let restartMessage = "Press Enter to restart...";
                if (this.game.restartRequest === true) {
                    restartMessage += " ✓";
                }
                this.drawTwoPartMessage("Game Over!", restartMessage);
            }
        }
    }

    drawPaddle(player) {
        if (player.isControlled) {
            this.ctx.fillStyle = "#fff";
        } else {
            this.ctx.fillStyle = "#a9a9a9";
        }
        this.ctx.fillRect(player.paddleX, player.paddleY, player.paddleWidth, player.paddleHeight);
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
        
        if (this.game.playerNb > 2) {
            // Scores for more than 2 players
            this.ctx.font = '60px "Geo", sans-serif';
            this.game.players.forEach((player) => {
                let x, y;
                
                switch (player.side) {
                    case 'left':
                        x = this.game.canvasWidth * 0.40; // Centered closer to the middle on the left side
                        y = this.game.canvasHeight / 2; // Centered vertically
                        break;
                        case 'right':
                            x = this.game.canvasWidth * 0.60; // Centered closer to the middle on the right side
                            y = this.game.canvasHeight / 2; // Centered vertically
                            break;
                            case 'up':
                        x = this.game.canvasWidth / 2; // Centered horizontally
                        y = this.game.canvasHeight * 0.40; // Centered closer to the middle on the top side
                        break;
                        case 'bottom':
                        x = this.game.canvasWidth / 2; // Centered horizontally
                        y = this.game.canvasHeight * 0.60; // Centered closer to the middle on the bottom side
                        break;
                    }
                    
                    // Ensure text is centered around the calculated x and y coordinates
                this.ctx.textAlign = 'center'; // Align text to be centered horizontally
                this.ctx.textBaseline = 'middle'; // Align text to be centered vertically
                
                this.ctx.fillText(player.score.toString(), x, y);
            });
        } else {
            // Original scoring logic for 2 players
            this.ctx.font = '100px "Geo", sans-serif';
            this.game.players.forEach((player) => {
                let x;
                const distanceFromCenter = this.game.canvasHeight * 0.20;
                const distanceFromTop = this.game.canvasHeight * 0.20;
                
                if (player.side === 'left') {
                    // Align the left player's score to the left of the center line
                    x = (this.game.canvasWidth / 2) - distanceFromCenter;
                } else {
                    // Align the right player's score to the right of the center line
                    x = (this.game.canvasWidth / 2) + distanceFromCenter;
                }
    
                // Use the fixed distance from the top for Y
                const y = distanceFromTop;
    
                this.ctx.fillText(player.score, x, y);
            });
        }
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

