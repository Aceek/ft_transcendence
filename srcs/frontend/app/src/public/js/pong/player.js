// player.js
export class Player {
    constructor(id, side, paddleWidth, paddleHeight, paddleSpeed, paddleY, score) {
        this.id = id;
        this.side = side;
        this.paddleWidth = paddleWidth;
        this.paddleHeight = paddleHeight;
        this.paddleSpeed = paddleSpeed;
        this.paddleY = paddleY;
        this.score = score;
      }
  
    //   setPaddleSide(side) {
    //       this.side = side;
    //   }

    handleStaticData(staticData) {
        // console.log(`Handling ${this.side} player static data`);
        this.paddleWidth = parseInt(staticData.paddleWidth, 10);
        this.paddleHeight = parseInt(staticData.paddleHeight, 10);
        this.paddleSpeed = parseInt(staticData.paddleSpeed, 10);
    }

    handleDynamicData(dynamicData) {
        // console.log(`Handling ${this.side} player dynamic data`);
        if (this.side === "left") {
            this.paddleY = parseInt(dynamicData.lp_y, 10);
            this.score = parseInt(dynamicData.lp_s, 10);
        } else if (this.side === "right") {
            this.paddleY = parseInt(dynamicData.rp_y, 10);
            this.score = parseInt(dynamicData.rp_s, 10);
        }
    }
}
