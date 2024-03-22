export class KeyEventController {
    constructor(socket, game) {
        this.socket = socket;
        this.game = game;
        this.initEventListeners();
    }

    initEventListeners() {
        document.addEventListener("keydown", (event) => this.handleKeyDown(event.key));
        document.addEventListener("keyup", (event) => this.handleKeyUp(event.key));
    }

    handleKeyDown(key) {
        this.game.playersToControl.forEach(player => {
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
        this.game.playersToControl.forEach(player => {
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
        
        switch (this.game.type) {
            case "tournament":
                this.handleTournamentMode();
                break;
            case "standard":
                this.handleStandardMode();
                break;
            default:
                console.log("Unknown game type.");
        }
    }
    
    handleTournamentMode() {
        console.log(this.game.mode);
        const basePath = this.game.mode === "online" ? "/tournament/" : "/local/tournament";
        const tournamentPageUrl = this.game.mode === "online" ? basePath + this.game.tournamentId : basePath;
        window.location.href = tournamentPageUrl;
    }
    
    handleStandardMode() {
        this.socket.send(JSON.stringify({ type: "restart_game" }));
        this.game.restartRequest = true;
    }

    updatePaddlePosition(key, player) {
        if (this.game.status !== 1) return;
        const change = key === player.moveDownKey ? player.paddleSpeed : -player.paddleSpeed;
        const newPos = player[player.paddleProp] + change;
        
        if (this.checkForPaddleCollision(player, newPos)) {
            return;
        }

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

    checkForPaddleCollision(movingPlayer, newPos) {
        const otherPlayers = this.game.players.filter(p => p.id !== movingPlayer.id);
        for (let otherPlayer of otherPlayers) {
            if (movingPlayer.paddleProp === 'paddleY') {
                if (newPos < otherPlayer.paddleY + otherPlayer.paddleHeight &&
                    newPos + movingPlayer.paddleHeight > otherPlayer.paddleY &&
                    movingPlayer.paddleX < otherPlayer.paddleX + otherPlayer.paddleWidth &&
                    movingPlayer.paddleX + movingPlayer.paddleWidth > otherPlayer.paddleX) {
                    return true;
                }
            } else {
                if (newPos < otherPlayer.paddleX + otherPlayer.paddleWidth &&
                    newPos + movingPlayer.paddleWidth > otherPlayer.paddleX &&
                    movingPlayer.paddleY < otherPlayer.paddleY + otherPlayer.paddleHeight &&
                    movingPlayer.paddleY + movingPlayer.paddleHeight > otherPlayer.paddleY) {
                    return true;
                }
            }
        }
        return false;
    }
}
