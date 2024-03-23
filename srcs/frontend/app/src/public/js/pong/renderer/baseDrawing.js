export class BaseDrawing {
    constructor(ctx) {
        this.ctx = ctx;
    }

    setFont(size, family = '"Geo", sans-serif') {
        this.ctx.font = `${size}px ${family}`;
    }

    setTextProperties(align = "center", baseline = "middle") {
        this.ctx.textAlign = align;
        this.ctx.textBaseline = baseline;
    }
    
    drawFilledRect(x, y, width, height, color) {
        this.ctx.fillStyle = color;
        this.ctx.fillRect(x, y, width, height);
    }
    
    drawText(text, x, y, color) {
        this.setShadowEffect();
        this.ctx.fillStyle = color;
        this.ctx.fillText(text, x, y);
        this.resetShadowEffect();
    }

    setShadowEffect() {
        this.ctx.shadowBlur = 10;
        this.ctx.shadowColor = 'rgba(0, 0, 0, 0.7)';
        this.ctx.shadowOffsetX = 5;
        this.ctx.shadowOffsetY = 5;
    }

    resetShadowEffect() {
        this.ctx.shadowBlur = 0;
        this.ctx.shadowOffsetX = 0;
        this.ctx.shadowOffsetY = 0;
    }
}
