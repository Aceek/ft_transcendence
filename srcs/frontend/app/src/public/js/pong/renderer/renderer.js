import { GameElements } from './gameElements.js';
import { GameMessages } from './gameMessages.js';

export class Renderer {
    constructor(ctx, game) {
        this.ctx = ctx;
        this.game = game;
        this.elements = new GameElements(ctx, game);
        this.messages = new GameMessages(ctx, game);
    }

    draw() {
        this.clearCanvas();
        this.elements.drawWhiteDashLine();
        this.messages.drawScores();
        this.messages.drawPerformanceMetrics();
        
        if (this.game.status !== -1) {
            this.drawGameActiveElements();
        }
        
        this.handleGameStatusMessages();

        if (this.game.receivedSide === "spectator") {
            this.messages.drawSpectatorModeMessage();
        }
    }

    clearCanvas() {
        this.ctx.clearRect(0, 0, this.game.canvasWidth, this.game.canvasHeight);
    }

    drawGameActiveElements() {
        this.elements.drawBall(this.game.ball.x, this.game.ball.y);
        this.game.players.forEach(player => this.elements.drawPaddle(player));
    }
    
    handleGameStatusMessages() {
        if (this.game.countdown !== null && this.game.countdown > 0) {
            this.messages.drawCountdownMessages();
        } else {
            this.messages.drawStatusSpecificMessages();
        }
    }
}