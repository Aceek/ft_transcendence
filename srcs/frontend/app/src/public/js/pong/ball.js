// ball.js
export class Ball {
    constructor(size, x, y, vx, vy) {
      this.size = size;
      this.x = x;
      this.y = y;
      this.vx = vx;
      this.vy = vy;
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
  