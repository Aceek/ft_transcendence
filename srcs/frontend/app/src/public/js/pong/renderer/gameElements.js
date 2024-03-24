import { BaseDrawing } from './baseDrawing.js';

export class GameElements extends BaseDrawing {
    constructor(ctx, game) {
        super(ctx);
        this.game = game;
    }

    drawBall(x, y) {
        this.setShadowEffect();
        this.drawFilledRect(x - this.game.ball.size / 2, y - this.game.ball.size / 2, this.game.ball.size, this.game.ball.size, "#fff");
        this.resetShadowEffect();
    }

    drawPaddle(player) {
        let color = player.color;
        
        if (this.game.status === 0 && player.isControlled) {
            const blink = Math.floor(Date.now() / 333) % 2 === 0;
            color = blink ? '#2D2D2D' : player.color;
            if (!blink) {
                this.setShadowEffect();
            }
        } else {
            this.setShadowEffect();
        }
        this.drawFilledRect(player.paddleX, player.paddleY, player.paddleWidth, player.paddleHeight, color);
        this.resetShadowEffect();
    }
    
    drawWhiteDashLine() {
        const dashColor = "rgba(255, 255, 255, 0.85)";
        this.ctx.strokeStyle = dashColor;
        this.ctx.lineWidth = 4;
        this.ctx.setLineDash([10, 7]);

        this.ctx.beginPath();
        this.ctx.moveTo(this.game.canvasWidth / 2, 0);
        this.ctx.lineTo(this.game.canvasWidth / 2, this.game.canvasHeight);
        this.ctx.stroke();
    }
}
