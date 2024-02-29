import { Ball } from './ball.js';

export class Game {
    constructor() {
        this.ball = new Ball();
        this.players = [];
        this.status = -1;
        this.canvasWidth = 0
        this.canvasHeight = 0
        this.countdown = null;
        this.controlledPlayer = null;
    }

    addPlayer(player) {
        this.players.push(player);
    }

    handleStaticData(staticData) {
        console.log("Received static data:", staticData);
        this.ball.handleStaticData(staticData);

        this.players.forEach(player => player.handleStaticData(staticData));

        this.canvasWidth = parseInt(staticData.canvasWidth, 10);
        this.canvasHeight = parseInt(staticData.canvasHeight, 10);
    }
  
    handleDynamicData(dynamicData) {
        console.log("Handling dynamic data:", dynamicData);
        this.ball.handleDynamicData(dynamicData);

        this.players.forEach(player => player.handleDynamicData(dynamicData));
        this.status = parseInt(dynamicData.gs, 10);
    }
    
    handlePaddleSideAssignment(paddleSide) {
        // Directly find and assign the controlled player based on the paddleSide
        const foundPlayer = this.players.find(player => player.side.toUpperCase() === paddleSide.toUpperCase());
        
        // If a matching player is found, mark them as the controlled player
        if (foundPlayer) {
            this.controlledPlayer = foundPlayer; // Assume there is a this.controlledPlayer property
            console.log(`Controlled player set to side: ${paddleSide}`);
        } else {
            console.log(`No player found with side: ${paddleSide}`);
        }
    }
    
    handleCountdown(seconds) {
        console.log("countdown :", seconds);
        this.countdown = seconds; // Use 'this' to refer to instance variable
    }
}
