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


    handleDynamicData(dynamicData, latency) {
      const serverX = parseFloat(dynamicData.b_x);
      const serverY = parseFloat(dynamicData.b_y);
      const vx = parseFloat(dynamicData.b_vx);
      const vy = parseFloat(dynamicData.b_vy);
  
      if (latency !== undefined && latency > 0) {
          const latencyInSeconds = latency / 1000;
          const adjustedX = serverX + vx * latencyInSeconds;
          const adjustedY = serverY + vy * latencyInSeconds;
  
          this.x = adjustedX;
          this.y = adjustedY;
      } else {
          this.x = serverX;
          this.y = serverY;
      }
  
      this.vx = vx;
      this.vy = vy;
  
      // Optional: Log for debugging
      // console.log(`Ball position - X: ${this.x}, Y: ${this.y}, Latency: ${latency ? latency + 'ms' : 'N/A'}`);
  }
  
    
}
  