export function updateOverlayPosition() {
	const canvas = document.getElementById('pongCanvas');
    const overlay = document.getElementById('scoreOverlay');
    if (!canvas || !overlay) return;

    const rect = canvas.getBoundingClientRect();

    overlay.style.position = 'fixed';
    overlay.style.left = `${rect.left}px`;
    overlay.style.top = `${rect.top}px`;
    overlay.style.width = `${canvas.offsetWidth}px`;
    overlay.style.height = `${canvas.offsetHeight}px`;
}

export function showScoreOverlay(color) {
    const overlay = document.getElementById('scoreOverlay');
    if (!overlay) return;

    updateOverlayPosition();

    // Set the overlay's background color to the assigned color and make it visible
    overlay.style.backgroundColor = color;
    overlay.style.display = 'block';
    overlay.style.opacity = '0.5';

    // Fade out and hide the overlay after a brief period
    setTimeout(() => overlay.style.opacity = '0', 250);
    setTimeout(() => overlay.style.display = 'none', 1000);
}


