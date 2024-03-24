export function extractRGB(color) {
    const match = color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
    return match ? { r: parseInt(match[1], 10), g: parseInt(match[2], 10), b: parseInt(match[3], 10) } : null;
}

export function updateGlowBaseColorFromRgba(rgbaColor) {
    const colorValues = extractRGB(rgbaColor);
    if (!colorValues) {
        console.error('Invalid color format:', rgbaColor);
        return;
    }
    
    document.documentElement.style.setProperty('--glow-intensity-1', `rgba(${colorValues.r}, ${colorValues.g}, ${colorValues.b}, 0.75)`);
    document.documentElement.style.setProperty('--glow-intensity-2', `rgba(${colorValues.r}, ${colorValues.g}, ${colorValues.b}, 0.6)`);
    document.documentElement.style.setProperty('--glow-intensity-3', `rgba(${colorValues.r}, ${colorValues.g}, ${colorValues.b}, 0.45)`);
    document.documentElement.style.setProperty('--glow-intensity-4', `rgba(${colorValues.r}, ${colorValues.g}, ${colorValues.b}, 0.3)`);
    document.documentElement.style.setProperty('--glow-intensity-5', `rgba(${colorValues.r}, ${colorValues.g}, ${colorValues.b}, 0.15)`);
}

export function assignColor(id) {
    const colors = [
        'rgba(0, 255, 255, 1)', // Turquoise/Cyan
        'rgba(255, 0, 255, 1)', // Purple
        'rgba(50, 255, 150, 1)', // Green
        'rgba(255, 165, 0, 1)', // Orange
        'rgba(255, 255, 255, 1)', // White
    ];
    return colors[id] || colors[4];
}
