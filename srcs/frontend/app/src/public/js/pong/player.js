import { updateGlowBaseColorFromRgba, assignColor } from './colorUtils.js';
import { showScoreOverlay } from './overlayEffects.js';

export class Player {
    constructor(id, side, isControlled, game) {
        this.id = id;
        this.side = side;
        this.isControlled = isControlled;
        this.game = game;
        this.initPaddleProperties();
        this.initKeyAndPositionProperties();
        this.paddleUpdateInterval = null;
        this.score = 0;
        this.scoreTmp = this.score;
        this.username = '';
        this.assignedColor = assignColor(id);
        this.color = this.assignedColor;
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
            if (this.game.mode == "offline") {
                this.moveUpKey = this.side === "left" ? "w" : "ArrowUp";
                this.moveDownKey = this.side === "left" ? "s" : "ArrowDown";
                this.moveUpKeySymbol = this.side === "left" ? "w" : "▲";
                this.moveDownKeySymbol = this.side === "left" ? "s" : "▼";
            } else if (this.game.mode == "online") {
                this.moveUpKey = "ArrowUp";
                this.moveDownKey = "ArrowDown";
                this.moveUpKeySymbol = "▲";
                this.moveDownKeySymbol = "▼";
            }
            this.paddleProp = 'paddleY';
            this.dimensionProp = 'paddleHeight';
        } else {
            this.moveUpKey = "ArrowLeft";
            this.moveDownKey = "ArrowRight";
            this.moveUpKeySymbol = "◄";
            this.moveDownKeySymbol = "►";
            this.paddleProp = 'paddleX';
            this.dimensionProp = 'paddleWidth';
        }
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
        if (this.score > this.scoreTmp) {
            this.handleScoreUpdate();
        }
        this.scoreTmp = this.score;
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

    handleScoreUpdate() {
        const canvas = document.getElementById('pongCanvas');
        if (!canvas) return;
    
        updateGlowBaseColorFromRgba(this.assignedColor);
        showScoreOverlay(this.assignedColor);
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
