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
  
  handleCompactedDynamicData(ball_data, avgPing, processTime, gameStatus) {
    const [serverX, serverY, serverVx, serverVy] = ball_data.map(parseFloat);
    
    const shouldAdjustForLatency = avgPing !== null && 
                                   processTime !== null &&
                                   gameStatus === 1;
    if (shouldAdjustForLatency) {
        const latencyInSeconds = (avgPing + processTime) / 1000;
        this.lastServerX = serverX + serverVx * latencyInSeconds;
        this.lastServerY = serverY + serverVy * latencyInSeconds;
    } else {
        this.lastServerX = serverX;
        this.lastServerY = serverY;
    }
    this.lastServerVx = serverVx;
    this.lastServerVy = serverVy;
    this.lastServerUpdate = Date.now();
  }
}
