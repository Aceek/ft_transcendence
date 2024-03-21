import { Ball } from './ball.js';
import { Player } from './player.js';

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
        this.restartRequest = false;
        this.isInitialized = false;
        this.countdown = null;
        this.latency = null;
        this.fps = null;
        this.processTime = null;

        // Game configuration properties
        this.canvasWidth = 0;
        this.canvasHeight = 0;
        this.playerNb = 0;
        this.mode = '';
        this.type = '';
        this.tournamentId = '';
        this.receivedSide = '';
    }

    initCanvas() {
        const canvas = document.getElementById('pongCanvas');
        this.canvas = canvas;
    }

    addPlayer(player) {
        this.players.push(player);
        if (player.isControlled) {
            this.controlledPlayer = player;
        }
    }

    createPlayers() {
        const sides = ['left', 'right', 'bottom', 'up'];
        for (let i = 0; i < this.playerNb; i++) {
            const playerSide = sides[i % sides.length];
            const isControlled = playerSide === this.receivedSide;
            const newPlayer = new Player(i, playerSide, isControlled);
            this.addPlayer(newPlayer);
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
    }
    
    handleDynamicData(dynamicData) {
        this.status = parseInt(dynamicData.gs, 10);
        if (this.status === 1) {
            this.restartRequest = false;
        }
        this.ball.handleDynamicData(dynamicData);
        this.players.forEach(player => player.handleDynamicData(dynamicData));
    }

    
    handleCompactedDynamicData(ball_data, players_data, process_time) {
        this.ball.handleCompactedDynamicData(ball_data, this.latency, this.processTime, this.status);
        this.players.forEach((player) => {
            player.handleCompactedDynamicData(players_data);
        });
        this.processTime = process_time;
        // console.log(this.processTime);
    }

    handlePaddleSideAssignment(paddleSide) {
        this.receivedSide = paddleSide.toLowerCase();
    }
    
    
    handleCountdown(seconds) {
        this.countdown = seconds;
    }
}
