import { userActivitySocket } from "./user_activity_websocket.js";

export function isChallengeModalOpen() {
  const challengeModal = document.getElementById("challengeModal");
  const challengeModalWaiting = document.getElementById(
    "challengeModalWaiting"
  );
  return (
    (challengeModal && challengeModal.classList.contains("show")) ||
    (challengeModalWaiting && challengeModalWaiting.classList.contains("show"))
  );
}

export function sendPing(socket) {
  if (socket === null || socket.readyState === WebSocket.CLOSED) {
    return;
  }
  socket.send(JSON.stringify({ action: "ping" }));
  setTimeout(() => sendPing(socket), 30000);
}

export function closeUserActivitySocket() {
  if (userActivitySocket && userActivitySocket.readyState === WebSocket.OPEN) {
    userActivitySocket.close();
  }
}

export function sendUserToTrack() {
  const userIds = extractUserIds();
  if (userIds.length === 0) {
    return;
  }
  sendTrackStatus(userIds);
}

export function extractUserIds() {
  const statusElements = document.querySelectorAll('[id^="status-"]');
  const userIds = Array.from(statusElements).map((el) => {
    return el.id.replace("status-", "");
  });
  return userIds;
}

export function setupButtonChallengeReceived(challengerId) {
  recreateButton("acceptChallenge");
  recreateButton("declineChallenge");

  const acceptButton = document.getElementById("acceptChallenge");
  const declineButton = document.getElementById("declineChallenge");

  acceptButton.onclick = function () {
    userActivitySocket.send(
      JSON.stringify({
        action: "challenge_response",
        challenger_id: challengerId,
        response: "accept",
      })
    );
    hideModal("challengeModal");
  };

  declineButton.onclick = function () {
    userActivitySocket.send(
      JSON.stringify({
        action: "challenge_response",
        challenger_id: challengerId,
        response: "decline",
      })
    );
    hideModal("challengeModal");
  };
}

function recreateButton(buttonId) {
  let oldButton = document.getElementById(buttonId);
  if (oldButton) {
    let newButton = oldButton.cloneNode(true);
    oldButton.parentNode.replaceChild(newButton, oldButton);
  }
}

function hideModal(modalId) {
  let modalElement = document.getElementById(modalId);
  if (modalElement) {
    let modalInstance = bootstrap.Modal.getInstance(modalElement);
    if (modalInstance) {
      modalInstance.hide();
    }
  }
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
