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
        this.ctx.fillStyle = color;
        this.ctx.fillText(text, x, y);
    }
}
