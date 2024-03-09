import { BaseDrawing } from './baseDrawing.js';

export class GameMessages extends BaseDrawing {
    constructor(ctx, game) {
        super(ctx);
        this.game = game;
    }

    drawCountdownMessages() {
        if (this.game.type === "tournament" && this.game.status === 2) {
            this.drawTwoPartMessage(this.game.countdown.toString(), "Opponent forfeiting in...");
        } else {
            this.drawPlayerNames();
            this.drawTwoPartMessage(this.game.countdown.toString(), "Get ready...");
        }
    }

    drawStatusSpecificMessages() {
        switch (this.game.status) {
            case 2:
                if (!(this.game.type === "tournament" && this.game.countdown === 0)) {
                    this.drawTwoPartMessage("Game Paused!",
                        "Waiting for other players to resume...");
                }
                break;
            case -1:
                this.drawTwoPartMessage("Room joined!",
                    "Waiting for other players to start...");
                break;
            case 3:
                this.drawGameOverMessages();
                break;
        }
    }

    drawGameOverMessages() {
        this.drawPlayerNames();
        if (this.game.type === "tournament") {
            this.drawTwoPartMessage("Game Over!",
                "Press Enter to go back to tournament page...");
        } else if (this.game.type === "standard") {
            let restartMessage = "Press Enter to restart...";
            if (this.game.restartRequest) {
                restartMessage += " ✓";
            }
            this.drawTwoPartMessage("Game Over!", restartMessage);
        }
    }
    
    drawTwoPartMessage(mainText, subText) {
        const gap = 50;
        this.setTextProperties();
        
        // Main Message
        this.setFont(70);
        const mainY = this.game.canvasHeight / 2 - gap;
        this.drawText(mainText, this.game.canvasWidth / 2, mainY, "#fff");
        
        // Sub Message
        this.setFont(30);
        const subY = mainY + gap * 2;
        this.drawText(subText, this.game.canvasWidth / 2, subY, "#fff");
    }
        
    drawScores() {
        this.setFont(100);
        this.game.players.forEach(player => {
            const { x, y } = this.calculateScorePosition(player);
            this.drawText(player.score.toString(), x, y, player.color);
        });
    }

    calculateScorePosition(player) {
        let x, y;
        const offset = this.game.canvasHeight * 0.20;
        switch (player.side) {
            case 'left':
                x = (this.game.canvasWidth / 2) - offset;
                y = offset;
                break;
            case 'right':
                x = (this.game.canvasWidth / 2) + offset;
                y = offset;
                break;
            case 'up':
            case 'bottom':
                x = this.game.canvasWidth / 2;
                y = (player.side === 'up') ? offset : this.game.canvasHeight - offset;
                break;
            }
            return { x, y };
    }
    
    drawPlayerNames() {
        this.game.players.forEach(player => {
            const { nameX, nameY } = this.getPlayerNamePosition(player);
            this.setFont(30);
            this.setTextProperties(player.side === 'left' ? "left" : 
                player.side === 'right' ? "right" : "center");
            this.drawText(player.username, nameX, nameY, player.color);
        });
    }

    getPlayerNamePosition(player) {
        let nameX, nameY;
        switch(player.side) {
            case 'left':
                nameX = player.paddleX + 30;
                nameY = player.paddleY + player.paddleHeight / 2;
                break;
            case 'right':
                nameX = player.paddleX + player.paddleWidth - 30;
                nameY = player.paddleY + player.paddleHeight / 2;
                break;
            case 'bottom':
                nameX = player.paddleX + player.paddleWidth / 2;
                nameY = player.paddleY - 30;
                break;
            case 'up':
                nameX = player.paddleX + player.paddleWidth / 2;
                nameY = player.paddleY + player.paddleHeight + 30;
                break;
            default:
                nameX = 10;
                nameY = 10;
                break;
        }
        return { nameX, nameY };
    }
}
