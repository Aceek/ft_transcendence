import { BaseDrawing } from './baseDrawing.js';

export class GameMessages extends BaseDrawing {
    constructor(ctx, game) {
        super(ctx);
        this.game = game;
    }

    drawCountdownMessages() {
        if (this.game.type === "tournament" && this.game.status === 2) {
            this.drawTwoPartMessage(this.game.countdown.toString(), 
            "Opponent forfeiting in...");
        } else {
            this.drawPlayerNames();
            this.drawTwoPartMessage(this.game.countdown.toString(),
            "Get ready...");
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
            case 4:
                this.drawNetworkIssuenMessages();
                break;
            case 5:
                this.drawServerDownMessages();
                break;
        }
    }

    drawGameOverMessages() {
        this.drawPlayerNames();
        if (this.game.receivedSide === "spectator") {
            this.drawTwoPartMessage("Game Over!", "");
        } else if (this.game.type === "tournament") {
            this.drawTwoPartMessage("Game Over!",
                "Press Enter to go to tournament page...");
        } else if (this.game.type === "standard") {
            let restartMessage = "Press Enter to restart...";
            if (this.game.restartRequest) {
                restartMessage += " ✓";
            }
            this.drawTwoPartMessage("Game Over!", restartMessage);
        }
    }

    drawNetworkIssueMessages() {
        this.setTextProperties();
        const mainMessage = "Network Issue";
        const subMessage = "Try refreshing or quit the page...";
        this.drawTwoPartMessage(mainMessage, subMessage);
    }
    
    drawServerDownMessages() {
        this.setTextProperties();
        const mainMessage = "Server Down";
        const subMessage = "Try refreshing or quit the page...";
        this.drawTwoPartMessage(mainMessage, subMessage);
    }
    drawTwoPartMessage(mainText, subText) {
        const gap = 50;
        this.setTextProperties();
        
        // Main Message
        this.setFont(80);
        const mainY = this.game.canvasHeight / 2 - gap;
        this.drawText(mainText, this.game.canvasWidth / 2, mainY, "#fff");
        
        // Sub Message
        this.setFont(35);
        const subY = mainY + gap * 2;
        this.drawText(subText, this.game.canvasWidth / 2, subY, "#fff");
    }
        
    drawScores() {
        this.setFont(100);
        this.game.players.forEach(player => {
            const { x, y } = this.calculateScorePosition(player);
            let align = this.getScoreAlignment(player);
            this.ctx.textAlign = align;
            if (player.score !== undefined && !isNaN(player.score)) {
                this.drawText(player.score.toString(), x, y, player.color);
            }
        });
        this.ctx.textAlign = 'left';
    }
    
    getScoreAlignment(player) {
        switch(player.side) {
            case 'left':
                return 'left';
            case 'right':
                return 'right';
            default:
                return 'center';
        }
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
    
    drawSpectatorModeMessage() {
        const message = "Spectator Mode";
        this.setTextProperties();
        this.setFont(30);
        
        const x = this.game.canvasWidth / 2;
        const y = this.game.canvasHeight - 30;
        
        this.drawText(message, x, y, "#fff", "center");
    }
    
    drawMetric(value, label, metricsY) {
        const separationSpacing = 10;
        const metricsX = this.game.canvasWidth - 40;
    
        const color = label === 'fps' ? (value < 50 ? '#B22222' : '#FFFFFF') : (value > 9 ? '#FF0000' : '#FFFFFF');
    
        this.ctx.textAlign = 'left';
        this.setFont(20);
        this.drawText(label, metricsX, metricsY, color);
    
        this.ctx.textAlign = 'right';
        this.setFont(20);
        let numberText = Math.round(value).toString();
        this.drawText(numberText, metricsX - separationSpacing, metricsY, color);
    }
    
    drawPerformanceMetrics() {
        this.setTextProperties();
        let metricsY = 15;
        
        this.ctx.textAlign = 'right';
        
        if (typeof this.game.fps === 'number') {
            this.drawMetric(this.game.fps, "fps", metricsY);
            metricsY += 20;
        }

        if (typeof this.game.avgPing === 'number') {
            const avgLatency = (this.game.status === 1 ? this.game.avgPing + this.game.processTime : this.game.avgPing);
            this.drawMetric(avgLatency, "ms", metricsY);
            metricsY += 20;
        }
    }
    
    drawGameInfo() {
        const infoSpacing = 20;
        let infoY = 15;
        const infoX = 10;
    
        this.setFont(20);
        this.ctx.fillStyle = "#fff";
        this.ctx.textAlign = 'left';
    
        this.drawText(`${this.game.mode} - ${this.game.type}`, infoX, infoY, "#fff");
        infoY += infoSpacing;
        this.drawText(`${this.game.scoreLimit} pts`, infoX, infoY, "#fff");
    }
    
    
    drawPaddleKeySymbols(player) {
        this.setTextProperties();
        const fontSize = 30;
        this.setFont(fontSize);
        
        if (player.side === 'left' || player.side === 'right') {
            let symbolX, symbolYUp, symbolYDown;
            symbolX = player.paddleX + player.paddleWidth / 2;
            symbolYUp = player.paddleY - 30;
            symbolYDown = player.paddleY + player.paddleHeight + 30;
            this.drawText(player.moveUpKeySymbol, symbolX, symbolYUp, player.color);
            this.drawText(player.moveDownKeySymbol, symbolX, symbolYDown, player.color);
        } else if (player.side === 'bottom' || player.side === 'up') {
            let symbolXUp, symbolXDown, symbolY;
            symbolXUp = player.paddleX - 30;
            symbolXDown = player.paddleX + player.paddleWidth + 30;
            symbolY = player.paddleY + player.paddleHeight / 2;
            this.drawText(player.moveUpKeySymbol, symbolXUp, symbolY, player.color);
            this.drawText(player.moveDownKeySymbol, symbolXDown, symbolY, player.color);
        }
    
    }
}
