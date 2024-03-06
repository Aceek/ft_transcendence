import { updateStatusOnPage } from "./user_activity_utils.js";
import {
  updateModalChallengeResponse,
  updateModalChallengeNoResponse,
  updateModalChallengeError,
  updateModalChallengeCanceled,
} from "./user_activity_modal.js";
import {
  injectModalChallengeReceived,
  injectModalChallengeWaiting,
} from "./user_activity_inject_modals.js";
import { userActivitySocket } from "./user_activity_websocket.js";
import { router } from "../main.js";

export function handleMessage(data) {
  if (data.action === "status_update") {
    updateStatusOnPage(data);
  } else if (data.action === "challenge_received") {
    handleChallengeReceived(data.challenger_id);
  } else if (data.action === "challenge_response") {
    handleChallengeResponse(data);
  } else if (data.action === "challenge_error") {
    hamdleChallengeError(data);
  } else if (data.action == "cancel_challenge") {
    handleChallengeCanceled(data);
  } else if (data.action == "pong") {
  } else {
    console.log("Unknown message from server: ", data);
  }
}

export async function handleSendChallenge(uid) {
  const websocket_user = userActivitySocket;
  if (
    websocket_user === null ||
    websocket_user.readyState === WebSocket.CLOSED
  ) {
    console.error("Websocket not connected");
    return;
  } else {
    await injectModalChallengeWaiting(uid);
    websocket_user.send(
      JSON.stringify({ action: "challenge_user", challenged_id: uid })
    );

    window.addEventListener("beforeunload", function (e) {
      websocket_user.send(
        JSON.stringify({ action: "cancel_challenge", challenged_id: uid })
      );
    });

    setTimeout(() => {
      updateModalChallengeNoResponse();
      userActivitySocket.send(
        JSON.stringify({ action: "cancel_challenge", challenged_id: uid })
      );
    }, 20000);
  }
}

export function handleChallengeResponse(data) {
  updateModalChallengeResponse(data);

  if (data.response === "accept" && data.room_url) {
    const url_room = data.room_url;
    router(url_room);
  }
}

export function hamdleChallengeError(data) {
  updateModalChallengeError(data);
}

export function handleChallengeCanceled(data) {
  updateModalChallengeCanceled(data);
}

export async function handleChallengeReceived(challengerId) {
  await injectModalChallengeReceived(challengerId);

  window.addEventListener("beforeunload", function (e) {
    userActivitySocket.send(
      JSON.stringify({
        action: "challenge_response",
        challenger_id: challengerId,
        response: "decline",
      })
    );
  });
}
