import { Ball } from './ball.js';
import { Player } from './player.js';
import { updateGlowBaseColorFromRgba } from './colorUtils.js';

export class Game {
    constructor() {
        this.initProperties();
        this.initCanvas();
    }

    initProperties() {
        this.ball = new Ball();
        this.players = [];
        this.status = -1;
        this.controlledPlayer = null;
        this.leftPlayer = null;
        this.rightPlayer = null;
        this.playersToControl = [];
        this.restartRequest = false;
        this.isInitialized = false;
        this.countdown = null;
        this.avgPing = null;
        this.fps = null;
        this.processTime = null;
        this.lastScoringPlayer = null;

        // Game configuration properties
        this.canvasWidth = 0;
        this.canvasHeight = 0;
        this.playerNb = 0;
        this.mode = '';
        this.type = '';
        this.tournamentId = '';
        this.receivedSides = [];
    }

    initCanvas() {
        const canvas = document.getElementById('pongCanvas');
        this.canvas = canvas;
    }

    addPlayer(player) {
        this.players.push(player);
        if (this.mode === 'online' && player.isControlled) {
            this.controlledPlayer = player;
        } else if (this.mode === 'offline') {
            if (player.isControlled && player.side === 'left') {
                this.leftPlayer = player;
            } else if (player.isControlled && player.side === 'right') {
                this.rightPlayer = player;
            }
        }
    }

    createPlayers() {
        const sides = ['left', 'right', 'bottom', 'up'];
        for (let i = 0; i < this.playerNb; i++) {
            const playerSide = sides[i % sides.length];
            const isControlled = this.receivedSides.includes(playerSide);
            const newPlayer = new Player(i, playerSide, isControlled, this);
            this.addPlayer(newPlayer);
        }
    }

    setPlayersToControl() {
        this.playersToControl = [];
    
        if (this.mode === 'online') {
            if (this.controlledPlayer) {
                this.playersToControl.push(this.controlledPlayer);
            }
        } else if (this.mode === 'offline') {
            if (this.leftPlayer) {
                this.playersToControl.push(this.leftPlayer);
            }
            if (this.rightPlayer) {
                this.playersToControl.push(this.rightPlayer);
            }
        }
    }
    
    updateCanvasSize() {
        this.canvas.width = this.canvasWidth;
        this.canvas.height = this.canvasHeight;
    }

    handleStaticData(staticData) {
        this.parseStaticData(staticData);
        this.updateCanvasSize();
        this.createPlayers();
        this.players.forEach(player => player.handleStaticData(staticData));
        this.ball.handleStaticData(staticData);
        if (!this.isInitialized) {
            this.isInitialized = true;
        }
    }

    parseStaticData(staticData) {
        this.playerNb = parseInt(staticData.playerNb, 10);
        this.canvasWidth = parseInt(staticData.canvasWidth, 10);
        this.canvasHeight = parseInt(staticData.canvasHeight, 10);
        this.mode = staticData.gameMode;
        this.type = staticData.gameType;
        this.tournamentId = staticData.tournamentId;
        this.scoreLimit = staticData.scoreLimit;
    }
    
    handleDynamicData(dynamicData) {
        this.status = parseInt(dynamicData.gs, 10);
        if (this.status === 0 || this.status === 1) {
            this.handleGameRestart();
        }
        this.ball.handleDynamicData(dynamicData);
        this.players.forEach(player => player.handleDynamicData(dynamicData));
    }

    handleGameRestart() {
        // Reset the canvas glow color to white when a game is restarting
        if (this.status === 0 && this.restartRequest === true) {
            updateGlowBaseColorFromRgba('rgba(255, 255, 255, 1)');
        }
        // Reset the restart request as the new game is ongoing
        if (this.status === 1 && this.restartRequest === true) {
            this.restartRequest = false;
        }
    }
    
    handleCompactedDynamicData(ball_data, players_data, process_time) {
        this.ball.handleCompactedDynamicData(ball_data, this.avgPing, this.processTime, this.status);
        this.players.forEach((player) => {
            if (!player.isControlled) {
                player.handleCompactedDynamicData(players_data);
            }
        });
        this.processTime = process_time;
    }
    
    handlePaddleSideAssignment(paddleSide) {
        const side = paddleSide.toLowerCase();
        if (!this.receivedSides.includes(side)) {
            this.receivedSides.push(side);
        }
    }
    
    handleCountdown(seconds) {
        this.countdown = seconds;
    }
}
