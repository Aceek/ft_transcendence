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


function handleMessage(data) {
  if (data.error) {
      console.error('Error from server: ', data.message);
  } else if (data.status === "pong") {
      console.log('Pong received from server');
  } else {
      console.log('Message from server: ', data);
  }
}

// utility function to send all uids of users with action = "track_status"
export function sendTrackStatus(user_ids) {
  if (userActivitySocket === null || userActivitySocket.readyState === WebSocket.CLOSED) {
    return;
  }
  userActivitySocket.send(JSON.stringify({action: "track_status", user_ids: user_ids}));
}
  
