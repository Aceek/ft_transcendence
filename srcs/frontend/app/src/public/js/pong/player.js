// player.js
export class Player {
    constructor(id, side) {
        this.id = id;
        this.side = side;
        this.paddleWidth = 0;
        this.paddleHeight = 0;
        this.paddleSpeed = 0;
        this.paddleX = 0;
        this.paddleY = 0;
        this.score = 0;
      }

    handleStaticData(staticData) {
        // console.log(`Handling ${this.side} player static data`);
        this.paddleWidth = parseInt(staticData.paddleWidth, 10);
        this.paddleHeight = parseInt(staticData.paddleHeight, 10);
        this.paddleSpeed = parseInt(staticData.paddleSpeed, 10);
    }

    handleDynamicData(dynamicData) {
        // console.log(`Handling ${this.side} player dynamic data`);
        if (this.side === "left") {
            this.paddleX = parseInt(dynamicData.lp_x, 10);
            this.paddleY = parseInt(dynamicData.lp_y, 10);
            this.score = parseInt(dynamicData.lp_s, 10);
        } else if (this.side === "right") {
            this.paddleX = parseInt(dynamicData.rp_x, 10);
            this.paddleY = parseInt(dynamicData.rp_y, 10);
            this.score = parseInt(dynamicData.rp_s, 10);
        } else if (this.side === "bottom") {
            this.paddleX = parseInt(dynamicData.bp_x, 10);
            this.paddleY = parseInt(dynamicData.bp_y, 10);
            this.score = parseInt(dynamicData.bp_s, 10);
        } else if (this.side === "up") {
            this.paddleX = parseInt(dynamicData.up_x, 10);
            this.paddleY = parseInt(dynamicData.up_y, 10);
            this.score = parseInt(dynamicData.up_s, 10);
        }
    }
}
