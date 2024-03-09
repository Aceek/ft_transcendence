export class KeyEventController {
    constructor(socket, game) {
        this.socket = socket;
        this.game = game;
        this.lastSentPaddlePos = null;
        this.initEventListeners();
    }

    initEventListeners() {
        document.addEventListener("keydown", (event) => this.handleKeyPress(event.key, true));
        document.addEventListener("keyup", (event) => this.handleKeyPress(event.key, false));
    }

    handleKeyPress(key, isPressed) {
        // Log every key press for debugging purposes
        // console.log(`Key Event: ${key}, Pressed: ${isPressed}`);
    
        // Exit early for key releases or if no player is controlled
        if (!isPressed || !this.game.controlledPlayer) {
            if (!isPressed) {
                console.log("Key released.");
            } else {
                console.log("Controlled player not found, exiting handleKeyPress");
            }
            return;
        }
    
        if (key === "Enter") {
            if (this.game.status === 3) {
                if (this.game.type === "tournament") {
                    // Assuming you have a way to get the tournament's page URL or ID
                    const tournamentPageUrl = `/tournament/${this.game.tournamentId}`; //
                    console.log("Redirecting to tournament page.");
                    window.location.href = tournamentPageUrl;
                    return;
                } else if (this.game.type === "standard") {
                    this.socket.send(JSON.stringify({ type: "restart_game" }));
                    console.log("Restart game message sent.");
                    this.game.restartRequest = true;
                    return;
                }
            }
        }
    
        if (this.game.status === 1) {
            this.updatePaddlePosition(key);
        }
    }

    updatePaddlePosition(key) {
        let change = this.game.controlledPlayer.paddleSpeed;
        const side = this.game.controlledPlayer.side;
    
        // Handle vertical movement for left/right sides
        if (side === 'left' || side === 'right') {
            let newY = this.game.controlledPlayer.paddleY + (key === "ArrowDown" ? change : key === "ArrowUp" ? -change : 0);
    
            // Check if the new Y position is within bounds
            if (newY >= 0 && (newY + this.game.controlledPlayer.paddleHeight) <= this.game.canvasHeight) {
                this.game.controlledPlayer.paddleY = newY;
                this.sendPaddlePositionUpdate(this.game.controlledPlayer);
                console.log(`Paddle Y updated: ${newY} for ${side}`);
            } else {
                console.log(`Y Out of bounds: ${newY}. Canvas height: ${this.game.canvasHeight}`);
            }
        }
    
        // Handle horizontal movement for bottom/up sides
        else if (side === 'bottom' || side === 'up') {
            let newX = this.game.controlledPlayer.paddleX + (key === "ArrowRight" ? change : key === "ArrowLeft" ? -change : 0);
    
            // Check if the new X position is within bounds
            if (newX >= 0 && (newX + this.game.controlledPlayer.paddleWidth) <= this.game.canvasWidth) {
                this.game.controlledPlayer.paddleX = newX;
                this.sendPaddlePositionUpdate(this.game.controlledPlayer);
                console.log(`Paddle X updated: ${newX} for ${side}`);
            } else {
                console.log(`X Out of bounds: ${newX}. Canvas width: ${this.game.canvasWidth}`);
            }
        }
    }
    
    sendPaddlePositionUpdate(player) {
        let currentPos;
        if (player.side === 'left' || player.side === 'right') {
            currentPos = player.paddleY;
        } else if (player.side === 'bottom' || player.side === 'up') {
            currentPos = player.paddleX;
        }
    
        if (this.lastSentPaddlePos !== currentPos) {
            console.log(`Sending paddle position update for ${player.side}: ${currentPos}`);
            this.socket.send(JSON.stringify({
                type: "update",
                pos: currentPos,
            }));
            this.lastSentPaddlePos = currentPos;
        } else {
            console.log("No significant change in paddle position. Not sending update.");
        }
    }
    
}
