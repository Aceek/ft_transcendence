import { Ball } from './ball.js';
import { Player } from './player.js';

export class Game {
    constructor() {
        this.ball = new Ball();
        this.players = [];
        this.status = -1;
        this.lastServerUpdate = 0;
        this.canvasWidth = 0
        this.canvasHeight = 0
        this.countdown = null;
        this.controlledPlayer = null;
        this.playerNb = 0;
    }

    addPlayer(player) {
        this.players.push(player);
    }

    handleStaticData(staticData) {
        console.log("Handling static data:", staticData);
        this.ball.handleStaticData(staticData);
    
        // Parsing static data to set up game dimensions and player number
        this.playerNb = parseInt(staticData.playerNb, 10);

        this.canvasWidth = parseInt(staticData.canvasWidth, 10);
        this.canvasHeight = parseInt(staticData.canvasHeight, 10);
        
        // Now, dynamically set the canvas size using the received dimensions
        const canvas = document.getElementById('pongCanvas'); // Ensure this ID matches your canvas element
        canvas.width = this.canvasWidth;
        canvas.height = this.canvasHeight;

        // Adjust the number of players based on playerNb
        const sides = ['left', 'right', 'bottom', 'up']; // Extend this array for more sides/players if needed
        for (let i = 0; i < this.playerNb; i++) {
            const playerId = i + 1; // Calculate player id as the next sequential number
            const playerSide = sides[i % sides.length]; // Assign player side, cycling through sides if necessary
    
            // Create and add the new player
            const newPlayer = new Player(playerId, playerSide);
            this.addPlayer(newPlayer);
    
            // Assign controlledPlayer if the player's side matches the received side
            if (playerSide === this.receivedSide) {
                this.controlledPlayer = newPlayer;
            }
            
        }
    
        // Pass static data to all players for their initialization
        this.players.forEach(player => player.handleStaticData(staticData));
    }
  
    handleDynamicData(dynamicData) {
        // console.log("Handling dynamic data:", dynamicData);
        this.ball.handleDynamicData(dynamicData);

        this.players.forEach(player => player.handleDynamicData(dynamicData));
        this.status = parseInt(dynamicData.gs, 10);
        this.lastServerUpdate = (new Date()).getTime();
    }
    
    handlePaddleSideAssignment(paddleSide) {
        this.receivedSide = paddleSide.toLowerCase();
    }
    
    handleCountdown(seconds) {
        console.log("countdown :", seconds);
        this.countdown = seconds; // Use 'this' to refer to instance variable
    }
}
