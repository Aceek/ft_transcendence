export class GameRenderer {
    constructor(ctx, game) {
        this.ctx = ctx;
        this.game = game;
    }

    draw() {
        const { ctx, game } = this;

        ctx.clearRect(0, 0, game.canvasWidth, game.canvasHeight);

        game.players.forEach(player => {
            const x = player.side === 'left' ? 0 : game.canvasWidth - player.paddleWidth;
            this.drawPaddle(x, player.paddleY, player.paddleWidth, player.paddleHeight);
        });

        this.drawBall(game.ball.x, game.ball.y);

        this.drawWhiteDashLine();

        this.drawScores();

        if (game.status === 2) {
            this.drawWaitingMessage();
        }

        if (game.status === 3) {
            this.drawGameOverMessage();
        }

        if (game.countdown !== null && game.countdown > 0) {
            ctx.font = "48px Arial";
            ctx.fillStyle = "red";
            ctx.textAlign = "center";
            ctx.fillText(game.countdown.toString(), game.canvasWidth / 2, game.canvasHeight / 2);
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
        const distanceFromCenter = 50;

        this.game.players.forEach((player) => {
            const textWidth = this.ctx.measureText(player.score).width;
            const x = player.side === 'left' ? (this.game.canvasWidth / 2) - distanceFromCenter - textWidth
                                            : (this.game.canvasWidth / 2) + distanceFromCenter;
            const y = this.game.canvasHeight / 6;

            this.ctx.fillText(player.score, x, y);
        });
    }

    drawGameOverMessage() {
        this.ctx.fillStyle = "#fff";
        this.ctx.font = '100px "Geo", sans-serif';
        const gameOverText = "Game Over!";
        const textWidth = this.ctx.measureText(gameOverText).width;
        const x = (this.game.canvasWidth / 2) - (textWidth / 2);
        const y = this.game.canvasHeight / 2;

        this.ctx.fillText(gameOverText, x, y);
    }

    drawWaitingMessage() {
        this.ctx.fillStyle = "#FFF";
        this.ctx.font = '30px Arial';
        this.ctx.textAlign = "center";
        this.ctx.fillText("Waiting for other players...", this.game.canvasWidth / 2, this.game.canvasHeight / 2);
    }
}
