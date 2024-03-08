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
        this.username = "";
        this.color = this.assignColor(id);
      }

    assignColor(id) {
        switch(id) {
            case 1:
                return '#008000'; // Green
            case 2:
                return '#FF0000'; // Red
            case 3:
                return '#0000FF'; // Blue
            case 4:
                return '#FFFF00'; // Yellow
            default:
                return '#FFF'; // Default color (White)
        }
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
    
    handleDynamicData(dynamicData) {
        // The 'side' dictates which part of 'dynamicData' to use
        switch (this.side) {
            case "left":
                this.paddleX = parseInt(dynamicData.lp_x, 10);
                this.paddleY = parseInt(dynamicData.lp_y, 10);
                this.score = parseInt(dynamicData.lp_s, 10);
                this.username = dynamicData.lp_u;
                break;
            case "right":
                this.paddleX = parseInt(dynamicData.rp_x, 10);
                this.paddleY = parseInt(dynamicData.rp_y, 10);
                this.score = parseInt(dynamicData.rp_s, 10);
                this.username = dynamicData.rp_u;
                break;
            case "bottom":
                this.paddleX = parseInt(dynamicData.bp_x, 10);
                this.paddleY = parseInt(dynamicData.bp_y, 10);
                this.score = parseInt(dynamicData.bp_s, 10);
                this.username = dynamicData.bp_u;
                break;
            case "up":
                this.paddleX = parseInt(dynamicData.up_x, 10);
                this.paddleY = parseInt(dynamicData.up_y, 10);
                this.score = parseInt(dynamicData.up_s, 10);
                this.username = dynamicData.up_u;
                break;
        }
    }

    handleCompactedDynamicData(pos) {
        switch (this.side) {
            case "left":
                this.paddleY = parseInt(pos, 10);
                break;
            case "right":
                this.paddleY = parseInt(pos, 10);
                break;
            case "bottom":
                this.paddleX = parseInt(pos, 10);
                break;
            case "up":
                this.paddleX = parseInt(pos, 10);
                break;
        }
    }
}
