let userActivitySocket = null;

export async function handleUserActivity() {
  if (
    userActivitySocket === null ||
    userActivitySocket.readyState === WebSocket.CLOSED
  ) {
    connectUserActivitySocket();
  }
}

function connectUserActivitySocket() {
  userActivitySocket = new WebSocket(
    "wss://" + window.location.host + "/ws/user_activity/"
  );

  userActivitySocket.onopen = function (e) {
    console.log("User activity socket connected");
    sendPing(userActivitySocket);
  };

  userActivitySocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    handleMessage(data);
  };

  userActivitySocket.onclose = function (e) {
    console.error(
      "User activity socket closed unexpectedly trying to reconnect"
    );
    userActivitySocket = null;
    setTimeout(() => connectUserActivitySocket(), 5000);
  };

  userActivitySocket.onerror = function (error) {
    console.error("User activity socket encountered error: ", error.message);
  };

  return userActivitySocket;
}

function sendPing(socket) {
  if (socket === null || socket.readyState === WebSocket.CLOSED) {
    return;
  }
  socket.send(JSON.stringify({ action: "ping" }));
  setTimeout(() => sendPing(socket), 30000);
}

export function updateStatusOnPage(data) {
  const statusElement = document.querySelector(`#status-${data.user_id}`);
  if (statusElement) {
    statusElement.textContent = `• ${data.status}`;

    statusElement.classList.remove("text-success", "text-danger");
    const statusClass =
      data.status === "online" ? "text-success" : "text-danger";
    statusElement.classList.add(statusClass);
  }
}

function handleMessage(data) {
  if (data.error) {
    console.error("Error from server: ", data.message);
  } else if (data.action === "status_update") {
    updateStatusOnPage(data);
  }
}

export function sendTrackStatus(user_ids) {
  if (
    userActivitySocket === null ||
    userActivitySocket.readyState === WebSocket.CLOSED
  ) {
    return;
  }
  userActivitySocket.send(
    JSON.stringify({ action: "track_status", user_ids: user_ids })
  );
}
