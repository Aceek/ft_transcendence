import { sendPing, sendUserToTrack } from "./user_activity_utils.js";
import { handleMessage } from "./user_activity_handle.js";

export let userActivitySocket = null;

export function connectUserActivitySocket() {
  userActivitySocket = new WebSocket(
    "wss://" + window.location.host + "/ws/user_activity/"
  );

  userActivitySocket.onopen = function (e) {
    sendPing(userActivitySocket);
    sendUserToTrack();
  };

  userActivitySocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    if (data.error === "anonymous_user") {
      userActivitySocket.close();
      userActivitySocket = null;
      return;
    }
    handleMessage(data);
  };

  userActivitySocket.onclose = function (e) {
    if (!userActivitySocket) {
      return;
    }
    setTimeout(() => connectUserActivitySocket(), 5000);
  };

  userActivitySocket.onerror = function (error) {
    console.error("User activity socket encountered error: ", error.message);
  };

  return userActivitySocket;
}
