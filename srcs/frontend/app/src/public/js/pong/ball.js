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
        this.x = parseInt(dynamicData.b_x, 10);
        this.y = parseInt(dynamicData.b_y, 10);
        this.vx = parseInt(dynamicData.b_vx, 10);
        this.vy = parseInt(dynamicData.b_vy, 10);
    
      }
  }
  