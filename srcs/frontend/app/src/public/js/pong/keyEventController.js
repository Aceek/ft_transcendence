export class KeyEventController {
    constructor(socket, game) {
        this.socket = socket;
        this.game = game;
        this.initEventListeners();
    }

    initEventListeners() {
        document.addEventListener("keydown", (event) => this.handleKeyDown(event.key));
        // document.addEventListener("keyup", (event) => this.handleKeyUp(event.key));
    }

    handleKeyDown(key) {
        if (!this.game.controlledPlayer) return;

        switch (key) {
            case "Enter":
                this.handleEnterKey();
                break;
            case "ArrowUp":
            case "ArrowDown":
                this.updateVerticalPaddlePosition(key);
                break;
            case "ArrowLeft":
            case "ArrowRight":
                this.updateHorizontalPaddlePosition(key);
                break;
            default:
                break;
        }
    }

    // handleKeyUp(key) {
    //     console.log("Key released:", key);
    // }
    
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

    updateVerticalPaddlePosition(key) {
        if (this.game.status !== 1) return;
        if (!['left', 'right'].includes(this.game.controlledPlayer.side)) return;

        const change = key === "ArrowDown" ? this.game.controlledPlayer.paddleSpeed : 
            -this.game.controlledPlayer.paddleSpeed;
        this.updatePaddlePosition(change, 'Y');
    }

    updateHorizontalPaddlePosition(key) {
        if (this.game.status !== 1) return;
        if (!['bottom', 'up'].includes(this.game.controlledPlayer.side)) return;

        const change = key === "ArrowRight" ? this.game.controlledPlayer.paddleSpeed :
            -this.game.controlledPlayer.paddleSpeed;
        this.updatePaddlePosition(change, 'X');
    }

    updatePaddlePosition(change, axis) {
        const paddleProp = axis === 'Y' ? 'paddleY' : 'paddleX';
        const dimensionProp = axis === 'Y' ? 'paddleHeight' : 'paddleWidth';
        const canvasDimension = axis === 'Y' ? this.game.canvasHeight : this.game.canvasWidth;

        let newPos = this.game.controlledPlayer[paddleProp] + change;

        if (newPos >= 0 && newPos + this.game.controlledPlayer[dimensionProp] <= canvasDimension) {
            this.game.controlledPlayer[paddleProp] = newPos;
            this.sendPaddlePositionUpdate();
        }
    }

    sendPaddlePositionUpdate() {
        const player = this.game.controlledPlayer;
        let currentPos = ['left', 'right'].includes(player.side) ? player.paddleY :
            player.paddleX;

        if (this.lastSentPaddlePos !== currentPos) {
            this.socket.send(JSON.stringify({ type: "update", pos: currentPos }));
            this.lastSentPaddlePos = currentPos;
        }
    }
}
