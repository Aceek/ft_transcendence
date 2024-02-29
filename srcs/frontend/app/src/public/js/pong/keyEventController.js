export class KeyEventController {
    constructor(socket, game) {
        this.socket = socket;
        this.game = game;
        this.lastSentPaddleY = null;
        this.initEventListeners();
    }

    initEventListeners() {
        document.addEventListener("keydown", (event) => this.handleKeyPress(event.key, true));
        document.addEventListener("keyup", (event) => this.handleKeyPress(event.key, false));
    }

    handleKeyPress(key, isPressed) {
        // Log every key press for debugging purposes
        console.log(`Key Event: ${key}, Pressed: ${isPressed}`);
    
        // Exit early for key releases or if no player is controlled
        if (!isPressed || !this.game.controlledPlayer) {
            if (!isPressed) {
                console.log("Key released.");
            } else {
                console.log("Controlled player not found, exiting handleKeyPress");
            }
            return;
        }
    
        // Handle game restart on 'Enter'
        if (key === "Enter" && this.game.status === 3) {
            this.socket.send(JSON.stringify({ type: "restart_game" }));
            console.log("Restart game message sent.");
            return;
        }
    
        // Only proceed to update paddle position for active game status
        if (this.game.status === 1) {
            this.updatePaddlePosition(key);
        }
    }
    
    updatePaddlePosition(key) {
        let change = this.game.controlledPlayer.paddleSpeed;
        let newY = this.game.controlledPlayer.paddleY + (key === "ArrowDown" ? change : -change);
    
        // Check if the new position is within bounds
        if (newY >= 0 && (newY + this.game.controlledPlayer.paddleHeight) <= this.game.canvasHeight) {
            this.game.controlledPlayer.paddleY = newY;
            this.sendPaddlePositionUpdate(this.game.controlledPlayer);
            console.log(`Paddle updated: ${newY} for ${this.game.controlledPlayer.side}`);
        } else {
            console.log(`Out of bounds: ${newY}. Canvas height: ${this.game.canvasHeight}`);
        }
    }

    sendPaddlePositionUpdate(player) {
        if (this.lastSentPaddleY != player.paddleY) {
            console.log(`Sending paddle position update for ${player.side}: ${player.paddleY}`);
            this.socket.send(JSON.stringify({
                type: "paddle_position_update",
                side: player.side,
                PaddleY: player.paddleY,
            }));
            this.lastSentPaddleY = player.paddleY;
        } else {
            console.log("No significant change in paddle position. Not sending update.");
        }
    }
}
