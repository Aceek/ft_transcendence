import { BaseDrawing } from './baseDrawing.js';

export class GameElements extends BaseDrawing {
    constructor(ctx, game) {
        super(ctx);
        this.game = game;
    }

    drawBall(x, y) {
        this.drawFilledRect(x - this.game.ball.size / 2, y - this.game.ball.size / 2, this.game.ball.size, this.game.ball.size, "#fff");
        // console.log(`DRAW - X: ${x}, Y: ${y}`);
    }

    drawPaddle(player) {
        this.drawFilledRect(player.paddleX, player.paddleY, player.paddleWidth, player.paddleHeight, player.color);
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
}
