export class KeyEventController {
    constructor(socket, game) {
        this.socket = socket;
        this.game = game;
        this.playersToControl = [];
        this.initEventListeners();
    }

    setPlayersToControl() {
        this.playersToControl = [];
    
        if (this.game.mode === 'online') {
            if (this.game.controlledPlayer) {
                this.playersToControl.push(this.game.controlledPlayer);
            }
        } else if (this.game.mode === 'offline') {
            if (this.game.leftPlayer) {
                this.playersToControl.push(this.game.leftPlayer);
            }
            if (this.game.rightPlayer) {
                this.playersToControl.push(this.game.rightPlayer);
            }
        }
    }

    initEventListeners() {
        document.addEventListener("keydown", (event) => this.handleKeyDown(event.key));
        document.addEventListener("keyup", (event) => this.handleKeyUp(event.key));
    }

    handleKeyDown(key) {
        this.playersToControl.forEach(player => {
            if ([player.moveUpKey, player.moveDownKey].includes(key)) {
                if (!player.paddleUpdateInterval) {
                    player.paddleUpdateInterval = setInterval(() => {
                        this.updatePaddlePosition(key, player);
                    }, 33);
                }
            }
        });

        if (key === "Enter") {
            this.handleEnterKey();
        }
    }

    handleKeyUp(key) {
        this.playersToControl.forEach(player => {
            if ([player.moveUpKey, player.moveDownKey].includes(key)) {
                if (player.paddleUpdateInterval) {
                    clearInterval(player.paddleUpdateInterval);
                    player.paddleUpdateInterval = null;
                }
            }
        });
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

    updatePaddlePosition(key, player) {
        if (this.game.status !== 1) return;
        const change = key === player.moveDownKey ? player.paddleSpeed : -player.paddleSpeed;
        const newPos = player[player.paddleProp] + change;
        
        const canvasDimension = player.paddleProp === 'paddleY' ? this.game.canvasHeight : this.game.canvasWidth;
            if (newPos >= 0 && newPos + player[player.dimensionProp] <= canvasDimension) {
                player[player.paddleProp] = newPos;
                this.sendPaddlePositionUpdate(player);
            }
        }
    
    sendPaddlePositionUpdate(player) {
        const currentPos = player[player.paddleProp];
        
        if (this.lastSentPaddlePos !== currentPos) {
            this.socket.send(JSON.stringify({ type: "update", pos: currentPos, side: player.side }));
            this.lastSentPaddlePos = currentPos;
        }
    }
}
