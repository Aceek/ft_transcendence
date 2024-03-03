let userActivitySocket = null;

export async function handleUserActivity() {

  if (userActivitySocket === null || userActivitySocket.readyState === WebSocket.CLOSED) {
    const userActivitySocket = connectUserActivitySocket();
  } else {
    console.log('User activity socket already exists');
  }

  
}


function connectUserActivitySocket() {
  userActivitySocket = new WebSocket(
      'wss://' + window.location.host + '/ws/user_activity/'
  );

  userActivitySocket.onopen = function(e) {
      console.log('User activity socket connected');
      sendPing(userActivitySocket); // Envoyer un ping initial
  };

  userActivitySocket.onmessage = function(e) {
      const data = JSON.parse(e.data);
      handleMessage(data);
  };

  userActivitySocket.onclose = function(e) {
      console.error('User activity socket closed unexpectedly');
  };

  userActivitySocket.onerror = function(error) {
      console.error('User activity socket encountered error: ', error.message);
  };

  return userActivitySocket;
}

function sendPing(socket) {
  console.log('Sending ping to server');
  socket.send(JSON.stringify({action: "ping"}));
  setTimeout(() => sendPing(socket), 30000);
}


export function updateStatusOnPage(data) {
  const statusElement = document.querySelector(`#status-${data.user_id}`);
  if (statusElement) {
    statusElement.textContent = `• ${data.status}`;

    statusElement.classList.remove("text-success", "text-danger");
    const statusClass = data.status === "online" ? "text-success" : "text-danger";
    statusElement.classList.add(statusClass);
  }
}


function handleMessage(data) {
  if (data.error) {
      console.error('Error from server: ', data.message);
  } else if (data.action === "pong") {
      console.log('Pong received from server');
  } else if (data.action === "status_update") {
      console.log('Status update received from server: ', data);
      updateStatusOnPage(data);

  } else {
      console.log('Message from server: ', data);
  }
}

export function sendTrackStatus(user_ids) {
  if (userActivitySocket === null || userActivitySocket.readyState === WebSocket.CLOSED) {
    return;
  }
  userActivitySocket.send(JSON.stringify({action: "track_status", user_ids: user_ids}));
}
  
