let lastDataTimestamp = 0; // Initialize outside the function to persist across calls
export class Ball {
    constructor() {
      this.size = 0;
      this.x = 0;
      this.y = 0;
      this.vx = 0;
      this.vy = 0;
    }
  
    handleStaticData(staticData) {
        this.size = parseInt(staticData.ballSize, 10);
    }

    handleDynamicData(dynamicData) {
      this.x = parseFloat(dynamicData.b_x);
      this.y = parseFloat(dynamicData.b_y);
      this.vx = parseFloat(dynamicData.b_vx);
      this.vy = parseFloat(dynamicData.b_vy);
  }
  
  handleCompactedDynamicData(ball_data, latency, processTime, gameStatus) {
      
    //   // Capture the current timestamp as soon as data is received
    //   const currentTimestamp = Date.now();
      
    //   // Calculate the delta time since the last data was received, in milliseconds
    //   const deltaTimeMs = lastDataTimestamp ? currentTimestamp - lastDataTimestamp : 0;
      
    //   // Update lastDataTimestamp for the next call
    //   lastDataTimestamp = currentTimestamp;
      
    //   console.log(`Delta: ${deltaTimeMs - 16.67}ms`);
    //   console.log(ball_data);
    //   console.log(`Latency: ${latency}ms`);
    const serverX = parseFloat(ball_data[0]);
    const serverY = parseFloat(ball_data[1]);
    const vx = parseFloat(ball_data[2]);
    const vy = parseFloat(ball_data[3]);
    
    if (latency == null || processTime == null || gameStatus !== 1) {
      this.x = serverX;
      this.y = serverY;
    } else {
      const latencyInSeconds = (latency + processTime) / 1000;
      const adjustedX = serverX + vx * latencyInSeconds;
      const adjustedY = serverY + vy * latencyInSeconds;
      
      this.lastServerX = adjustedX;
      this.lastServerY = adjustedY;
    }
    this.vx = vx;
    this.vy = vy;

    // console.log(`SERV - X: ${this.x}, Y: ${this.y}, lantency ${latency}`);

    this.lastServerUpdate = Date.now();
  }
}
