import { Ball } from './ball.js';
import { Player } from './player.js';

export class Game {
    constructor() {
        this.ball = new Ball();
        this.players = [];
        this.controlledPlayer = null;
        this.status = -1;
        this.isInitialized = false;
        this.restartRequest = false;

        this.lastServerUpdate = 0;
        this.latency = null
        this.countdown = null;

        this.canvasWidth = 0
        this.canvasHeight = 0
        
        this.gameMode = '';
        this.playerNb = 0;
        this.gameType = '';
        this.tournamentId = '';
        this.gameID = '';
        this.receivedSide = '';
    }

    addPlayer(player) {
        this.players.push(player);
    }

    handleStaticData(staticData) {
        // console.log("Handling static data:", staticData);
        
        this.playerNb = parseInt(staticData.playerNb, 10);
        this.canvasWidth = parseInt(staticData.canvasWidth, 10);
        this.canvasHeight = parseInt(staticData.canvasHeight, 10);
        this.mode = staticData.gameMode;
        this.type = staticData.gameType;
        this.matchID = staticData.matchID;
        this.tournamentId = staticData.tournamentId;
        
        const canvas = document.getElementById('pongCanvas');
        canvas.width = this.canvasWidth;
        canvas.height = this.canvasHeight;
        
        const sides = ['left', 'right', 'bottom', 'up']; // Adjust as needed
        for (let i = 0; i < this.playerNb; i++) {
            const playerId = i + 1;
            const playerSide = sides[i % sides.length];
            const isControlled = playerSide === this.receivedSide;
            
            const newPlayer = new Player(playerId, playerSide, isControlled);
            this.addPlayer(newPlayer);
            if (isControlled) {
                this.controlledPlayer = newPlayer;
            }
        }

        this.players.forEach(player => player.handleStaticData(staticData));
        this.ball.handleStaticData(staticData);

        this.isInitialized = true;
    }
    
    handleDynamicData(dynamicData, serverTimestamp) {
        console.log("Handling dynamic data:", dynamicData);
        // Convert server timestamp from seconds to milliseconds
        const serverTimestampMs = parseInt(serverTimestamp, 10);
        const currentTime = (new Date()).getTime();
        
        // Calculate the network latency
        this.latency = currentTime - serverTimestampMs;
        this.lastServerUpdate = currentTime - this.latency;
        // console.log("Network latency: ", this.latency, "ms");
        
        this.status = parseInt(dynamicData.gs, 10);
        this.ball.handleDynamicData(dynamicData, this.latency, this.status);
        this.players.forEach(player => player.handleDynamicData(dynamicData));
    }

    handlePaddleSideAssignment(paddleSide) {
        this.receivedSide = paddleSide.toLowerCase();
    }
    
    handleCountdown(seconds) {
        console.log("countdown :", seconds);
        this.countdown = seconds;
    }
}
