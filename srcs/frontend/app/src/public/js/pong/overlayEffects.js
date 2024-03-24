export function showScoreOverlay(assignedColor) {
    const canvas = document.getElementById('pongCanvas');
    const overlay = document.getElementById('scoreOverlay');

    if (!canvas || !overlay) return;

    // Match the overlay's position and size with the canvas
    const rect = canvas.getBoundingClientRect();
    overlay.style.position = 'absolute';
    overlay.style.left = `${rect.left}px`;
    overlay.style.top = `${rect.top}px`;
    overlay.style.width = `${canvas.offsetWidth}px`;
    overlay.style.height = `${canvas.offsetHeight}px`;

    // Set the overlay's background color to the assigned color
    overlay.style.backgroundColor = assignedColor;
    overlay.style.display = 'block';
    overlay.style.opacity = '0.5';

    // Fade out and hide the overlay after a brief period
    setTimeout(() => overlay.style.opacity = '0', 250);
    setTimeout(() => overlay.style.display = 'none', 1000);
}
