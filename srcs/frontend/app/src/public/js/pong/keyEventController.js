export class KeyEventController {
    constructor(socket, game) {
        this.socket = socket;
        this.game = game;
        this.throttleRate = 60;
        this.lastUpdateSentTime = 0;
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
        if (!this.game.controlledPlayer) {
            console.log("Controlled player not found, exiting handleKeyPress");
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
            if (!isPressed) {
                this.sendPaddlePositionUpdate(this.game.controlledPlayer, true); // Force update on key release
                console.log("Key released. Sending final paddle position update.");
                return;
            }
        }
    }

    updatePaddlePosition(key) {
        let change = this.game.controlledPlayer.paddleSpeed;
        const side = this.game.controlledPlayer.side;
    
        // Calculate new position based on key press
        let newX = this.game.controlledPlayer.paddleX + (key === "ArrowRight" ? change : key === "ArrowLeft" ? -change : 0);
        let newY = this.game.controlledPlayer.paddleY + (key === "ArrowDown" ? change : key === "ArrowUp" ? -change : 0);
    
        // Update the paddle position immediately, but only within bounds
        if ((side === 'left' || side === 'right') && newY >= 0 && (newY + this.game.controlledPlayer.paddleHeight) <= this.game.canvasHeight) {
            this.game.controlledPlayer.paddleY = newY;
        } else if ((side === 'bottom' || side === 'up') && newX >= 0 && (newX + this.game.controlledPlayer.paddleWidth) <= this.game.canvasWidth) {
            this.game.controlledPlayer.paddleX = newX;
        }
    
        // Check if the new position is within bounds and if sufficient time has passed since the last update
        const now = Date.now();
        if (now - this.lastUpdateSentTime >= this.throttleRate) {
            // Since the position is always updated, we send the update here without rechecking bounds
            this.sendPaddlePositionUpdate(this.game.controlledPlayer);
            this.lastUpdateSentTime = now; // Update the timestamp of the last sent update
        } else {
            console.log("Consecutive position update sent too soon.");
        }
    }
    
    
    sendPaddlePositionUpdate(player, force = false) {
        let currentPos = player.side === 'left' || player.side === 'right' ? player.paddleY : player.paddleX;
        
        // Send update if there's a significant change or if forced (on key release)
        if (force || this.lastSentPaddlePos !== currentPos) {
            console.log(`Sending paddle position update: ${currentPos} for ${player.side}`);
            this.socket.send(JSON.stringify({
                type: "paddle_position_update",
                paddle_pos: currentPos,
            }));
            this.lastSentPaddlePos = currentPos; // Update the last sent position
        } else {
            console.log("No significant change in paddle position. Not sending update.");
        }
    }
}
