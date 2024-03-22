export class Player {
    constructor(id, side, isControlled, gameMode) {
        this.id = id;
        this.side = side;
        this.isControlled = isControlled;
        this.gameMode = gameMode;
        this.initPaddleProperties();
        this.initKeyAndPositionProperties();
        this.paddleUpdateInterval = null;
        this.score = 0;
        this.username = '';
        this.color = this.assignColor(id);
    }

    initPaddleProperties() {
        this.paddleWidth = 0;
        this.paddleHeight = 0;
        this.paddleSpeed = 0;
        this.paddleX = 0;
        this.paddleY = 0;
    }

    initKeyAndPositionProperties() {
        const isVertical = this.side === "left" || this.side === "right";
        if (isVertical) {
            if (this.gameMode == "offline") {
                this.moveUpKey = this.side === "left" ? "w" : "ArrowUp";
                this.moveDownKey = this.side === "left" ? "s" : "ArrowDown";
                this.moveUpKeySign = this.side === "left" ? "w" : "↑";
                this.moveDownKeySign = this.side === "left" ? "s" : "↓";
            } else if (this.gameMode == "online") {
                this.moveUpKey = "ArrowUp";
                this.moveDownKey = "ArrowDown";
                this.moveUpKeySign = "↑";
                this.moveDownKeySign = "↓";
            }
            this.paddleProp = 'paddleY';
            this.dimensionProp = 'paddleHeight';
        } else {
            this.moveUpKey = "ArrowLeft";
            this.moveDownKey = "ArrowRight";
            this.moveUpKeySign = "←";
            this.moveDownKeySign = "→";
            this.paddleProp = 'paddleX';
            this.dimensionProp = 'paddleWidth';
        }
    }
    

    assignColor(id) {
        // const colors = ['#008000', '#FF0000', '#0000FF', '#FFFF00', '#FFF']; // Classic Green, Red, Blue, Yellow, Default White
        const colors = ['#00FF00', '#FF0000', '#0000FF', '#FFFF00', '#FFFFFF']; // Bright Green, Bright Red, Bright Blue, Bright Yellow, White
        return colors[id] || colors[4];
    }

    handleStaticData(staticData) {
        this.adjustPaddleDimensions(staticData);
        this.paddleSpeed = parseInt(staticData.paddleSpeed, 10);
    }

    adjustPaddleDimensions(staticData) {
        const isVertical = this.side === "left" || this.side === "right";
        this.paddleWidth = parseInt(staticData[isVertical ? "paddleWidth" : "paddleHeight"], 10);
        this.paddleHeight = parseInt(staticData[isVertical ? "paddleHeight" : "paddleWidth"], 10);
    }

    handleDynamicData(dynamicData) {
        const sideData = this.getSideData(dynamicData);
        this.paddleX = parseInt(sideData.x, 10);
        this.paddleY = parseInt(sideData.y, 10);
        this.score = parseInt(sideData.score, 10);
        this.username = sideData.username;
    }

    getSideData(dynamicData) {
        const fieldMap = {
            left: { x: 'lp_x', y: 'lp_y', score: 'lp_s', username: 'lp_u' },
            right: { x: 'rp_x', y: 'rp_y', score: 'rp_s', username: 'rp_u' },
            bottom: { x: 'bp_x', y: 'bp_y', score: 'bp_s', username: 'bp_u' },
            up: { x: 'up_x', y: 'up_y', score: 'up_s', username: 'up_u' },
        };
        const fields = fieldMap[this.side];
        return {
            x: dynamicData[fields.x],
            y: dynamicData[fields.y],
            score: dynamicData[fields.score],
            username: dynamicData[fields.username],
        };
    }

    handleCompactedDynamicData(pos) {
        const isVertical = this.side === "left" || this.side === "right";
        if (isVertical) {
            this.paddleY = parseInt(pos[this.id], 10);
        } else {
            this.paddleX = parseInt(pos[this.id], 10);
        }
    }
}
