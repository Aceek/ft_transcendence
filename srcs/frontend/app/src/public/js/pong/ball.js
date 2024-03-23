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
    const serverX = parseFloat(ball_data[0]);
    const serverY = parseFloat(ball_data[1]);
    const vx = parseFloat(ball_data[2]);
    const vy = parseFloat(ball_data[3]);
    
    if (avgPing == null || processTime == null || gameStatus !== 1) {
      this.x = serverX;
      this.y = serverY;
    } else {
      const latencyInSeconds = (avgPing + processTime) / 1000;
      const adjustedX = serverX + vx * latencyInSeconds;
      const adjustedY = serverY + vy * latencyInSeconds;
      
      this.lastServerX = adjustedX;
      this.lastServerY = adjustedY;
    }
    this.vx = vx;
    this.vy = vy;
    this.lastServerUpdate = Date.now();
  }
}
