export function startSendingPing(pongSocket) {
    const id = setInterval(() => {
        if (pongSocket && pongSocket.readyState === WebSocket.OPEN) {
            pongSocket.send(JSON.stringify({
                type: "ping",
                timestamp: Date.now()
            }));
        }
        console.log("piing");
    }, 500);
    return id;
}

export function calculateAvgPing(currentAvgPing, dataTimestamp, alpha, thresholdMultiplier = 5) {
    const now = Date.now();
    const measuredPing = (now - dataTimestamp) / 2;
    if (currentAvgPing === null) {
        return measuredPing;
    }
    
    const threshold = currentAvgPing * thresholdMultiplier;
    if (measuredPing > threshold) {
        return currentAvgPing;
    }

    const newAvgPing = (alpha * measuredPing) + ((1 - alpha) * currentAvgPing);
    return newAvgPing;
}