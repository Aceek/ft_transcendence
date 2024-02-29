// ball.js
export class Ball {
    constructor() {
      this.size = 0;
      this.x = 0;
      this.y = 0;
      this.vx = 0;
      this.vy = 0;
    }
  
    handleStaticData(staticData) {
        // console.log("Handling ball static data");
        this.size = parseInt(staticData.ballSize, 10);
    }

    handleDynamicData(dynamicData) {
        // console.log("Handling ball dynamic data");
        this.x = parseFloat(dynamicData.b_x);
        this.y = parseFloat(dynamicData.b_y);
        this.vx = parseFloat(dynamicData.b_vx);
        this.vy = parseFloat(dynamicData.b_vy);
      }
  }
  