export class KeyEventController {
    constructor(socket, game) {
        this.socket = socket;
        this.game = game;
        this.paddleUpdateInterval = null;
        this.initEventListeners();
    }

    initEventListeners() {
        document.addEventListener("keydown", (event) => this.handleKeyDown(event.key));
        document.addEventListener("keyup", (event) => this.handleKeyUp(event.key));
    }

    handleKeyDown(key) {
        if (!this.game.controlledPlayer) return;

        switch (key) {
            case "Enter":
                this.handleEnterKey();
                break;
            case "ArrowUp":
            case "ArrowDown":
                if (!this.paddleUpdateInterval) {
                    this.paddleUpdateInterval = setInterval(() => {
                        this.updateVerticalPaddlePosition(key, this.game.controlledPlayer);
                    }, 33);
                }
                break;
            case "w":
            case "s":
                if (!this.paddleUpdateInterval) {
                    this.paddleUpdateInterval = setInterval(() => {
                        this.updateVerticalPaddlePosition(key, this.game.controlledPlayer);
                    }, 33);
                }
                break;
            case "ArrowLeft":
            case "ArrowRight":
                if (!this.paddleUpdateInterval) {
                    this.paddleUpdateInterval = setInterval(() => {
                        this.updateHorizontalPaddlePosition(key, this.game.controlledPlayer);
                    }, 33);
                }
                break;
            default:
                break;
        }
    }

    handleKeyUp(key) {
        if (key === "ArrowUp" || key === "ArrowDown" ||
            key === "w" || key === "s" ||
            key === "ArrowLeft" || key === "ArrowRight") {
            if (this.paddleUpdateInterval) {
                clearInterval(this.paddleUpdateInterval);
                this.paddleUpdateInterval = null;
            }
        }
    }
    
    handleEnterKey() {
        if (this.game.status !== 3) return;
        
        if (this.game.type === "tournament") {
            const tournamentPageUrl = `/tournament/${this.game.tournamentId}`;
            window.location.href = tournamentPageUrl;
        } else if (this.game.type === "standard") {
            this.socket.send(JSON.stringify({ type: "restart_game" }));
            this.game.restartRequest = true;
        }
    }

    updateVerticalPaddlePosition(key, player) {
        if (this.game.status !== 1) return;
        if (!['left', 'right'].includes(player.side)) return;

        const change = (key === "ArrowDown" || key === "s") ? player.paddleSpeed : (key === "ArrowUp" || key === "w") ? -player.paddleSpeed : 0;
        this.updatePaddlePosition(change, 'Y', player);
    }

    updateHorizontalPaddlePosition(key, player) {
        if (this.game.status !== 1) return;
        if (!['bottom', 'up'].includes(player.side)) return;

        const change = key === "ArrowRight" ? player.paddleSpeed : -player.paddleSpeed;
        this.updatePaddlePosition(change, 'X', player);
    }

    updatePaddlePosition(change, axis, player) {
        const paddleProp = axis === 'Y' ? 'paddleY' : 'paddleX';
        const dimensionProp = axis === 'Y' ? 'paddleHeight' : 'paddleWidth';
        const canvasDimension = axis === 'Y' ? this.game.canvasHeight : this.game.canvasWidth;

        let newPos = player[paddleProp] + change;

        if (newPos >= 0 && newPos + player[dimensionProp] <= canvasDimension) {
            this.game.controlledPlayer[paddleProp] = newPos;
            this.sendPaddlePositionUpdate(player);
        }
    }

    sendPaddlePositionUpdate(player) {
        let currentPos = ['left', 'right'].includes(player.side) ? player.paddleY : player.paddleX;
    
        if (this.lastSentPaddlePos !== currentPos) {
            // Include the 'side' field in the message
            this.socket.send(JSON.stringify({ type: "update", pos: currentPos, side: player.side }));
            this.lastSentPaddlePos = currentPos;
        }
    }
}
