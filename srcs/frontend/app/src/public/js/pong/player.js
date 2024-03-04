// player.js
export class Player {
    constructor(id, side, isControlled) {
        this.id = id;
        this.side = side;
        this.isControlled = isControlled;
        this.paddleWidth = 0;
        this.paddleHeight = 0;
        this.paddleSpeed = 0;
        this.paddleX = 0;
        this.paddleY = 0;
        this.score = 0;
      }

      handleStaticData(staticData) {
        switch (this.side) {
            case "left":
            case "right":
                this.paddleWidth = parseInt(staticData.paddleWidth, 10);
                this.paddleHeight = parseInt(staticData.paddleHeight, 10);
                break;
            case "bottom":
            case "up":
                this.paddleWidth = parseInt(staticData.paddleHeight, 10);
                this.paddleHeight = parseInt(staticData.paddleWidth, 10);
                break;
        }
    
        this.paddleSpeed = parseInt(staticData.paddleSpeed, 10);
    }
    

    handleDynamicData(dynamicData, initialSent = false) {
        switch (this.side) {
            case "left":
                if (!this.isControlled || initialSent) {
                    this.paddleY = parseInt(dynamicData.lp_y, 10);
                }
                this.paddleX = parseInt(dynamicData.lp_x, 10);
                this.score = parseInt(dynamicData.lp_s, 10);
                break;
            case "right":
                if (!this.isControlled || initialSent) {
                    this.paddleY = parseInt(dynamicData.rp_y, 10);
                }
                this.paddleX = parseInt(dynamicData.rp_x, 10);
                this.score = parseInt(dynamicData.rp_s, 10);
                break;
            case "bottom":
                if (!this.isControlled || initialSent) {
                    this.paddleX = parseInt(dynamicData.bp_x, 10);
                }
                this.paddleY = parseInt(dynamicData.bp_y, 10);
                this.score = parseInt(dynamicData.bp_s, 10);
                break;
            case "up":
                if (!this.isControlled || initialSent) {
                    this.paddleX = parseInt(dynamicData.up_x, 10);
                }
                this.paddleY = parseInt(dynamicData.up_y, 10);
                this.score = parseInt(dynamicData.up_s, 10);
                break;
        }
    }
    
}
