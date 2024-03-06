import { router } from "../main.js";
import { fetchTemplate } from "../pageUtils.js";

let userActivitySocket = null;

export function closeUserActivitySocket() {
  if (
    userActivitySocket &&
    userActivitySocket.readyState === WebSocket.OPEN
  ) {
    userActivitySocket.close();
  }
}

export async function handleUserActivity() {
  if (
    userActivitySocket === null ||
    userActivitySocket.readyState === WebSocket.CLOSED
  ) {
    connectUserActivitySocket();
  }
}

function sendUserToTrack() {
  const userIds = extractUserIds();
  if (userIds.length === 0) {
    return;
  }
  sendTrackStatus(userIds);
}

function extractUserIds() {
  const statusElements = document.querySelectorAll('[id^="status-"]');
  const userIds = Array.from(statusElements).map((el) => {
    return el.id.replace("status-", "");
  });
  return userIds;
}
function connectUserActivitySocket() {
  userActivitySocket = new WebSocket(
    "wss://" + window.location.host + "/ws/user_activity/"
  );

  userActivitySocket.onopen = function (e) {
    console.log("User activity socket connected");
    sendPing(userActivitySocket);
    sendUserToTrack();
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
  } else if (data.action === "challenge_received") {
    console.log("Challenge received from: ", data.challenger_id);
    handleChallengeReceived(data.challenger_id);
  } else if (data.action === "challenge_response") {
    handleChallengeResponse(data);
  } else if (data.action === "challenge_error") {
    hamdleChallengeError(data);
  } else if (data.action == "cancel_challenge") {
    handleChallengeCanceled(data);
    console.log("Challenge canceled by: ", data.challenger_id);
  } else {
    console.log("Unknown message from server: ", data);
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

async function updateModalChallengeNoResponse() {
  const modal = document.getElementById("challengeModalWaiting");

  if (!modal) {
    return;
  }

  const modalTitle = document.querySelector(
    "#challengeModalWaiting .modal-title"
  );
  const modalBody = document.querySelector(
    "#challengeModalWaiting .modal-body"
  );

  if (modalTitle) modalTitle.textContent = "Aucune réponse";

  if (modalBody)
    modalBody.innerHTML = `<p>L'adversaire n'a pas répondu au défi.</p>`;

  const cancelButton = document.getElementById("cancelWaiting");
  if (cancelButton) cancelButton.remove();

  setTimeout(() => {
    const waitingModalElement = document.getElementById(
      "challengeModalWaiting"
    );
    const waitingModal = bootstrap.Modal.getInstance(waitingModalElement);
    if (waitingModal) {
      waitingModal.hide();
      waitingModalElement.remove();
    }
  }, 3000);
}

async function injectModalChallengeWaiting(uid) {
  let existingModalElement = document.getElementById("challengeModalWaiting");

  if (existingModalElement) {
    existingModalElement.remove();
  }

  const modalHtml = await fetchTemplate(
    "/public/html/popup-challenge_waiting.html"
  );
  document.body.insertAdjacentHTML("beforeend", modalHtml);

  let myModal = new bootstrap.Modal(
    document.getElementById("challengeModalWaiting"),
    {
      keyboard: false,
      backdrop: "static",
    }
  );

  document
    .getElementById("cancelWaiting")
    .addEventListener("click", function () {
      console.log("Annulation du défi par l'utilisateur.");
      userActivitySocket.send(
        JSON.stringify({ action: "cancel_challenge", challenged_id: uid })
      );
      myModal.hide();
    });

  myModal.show();
}

async function handleChallengeReceived(challengerId) {
  // if (isChallengeModalOpen()) {
  //   userActivitySocket.send(
  //     JSON.stringify({
  //       action: "challenge_response",
  //       challenger_id: challengerId,
  //       response: "decline",
  //     })
  //   );
  //   return;
  // }
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

function isChallengeModalOpen() {
  const challengeModal = document.getElementById("challengeModal");
  const challengeModalWaiting = document.getElementById(
    "challengeModalWaiting"
  );
  return (
    (challengeModal && challengeModal.classList.contains("show")) ||
    (challengeModalWaiting && challengeModalWaiting.classList.contains("show"))
  );
}

async function injectModalChallengeReceived(challengerId) {
  let myModal = bootstrap.Modal.getInstance(
    document.getElementById("challengeModal")
  );

  if (!myModal) {
    const modalHtml = await fetchTemplate("/public/html/popup-challenge.html");
    document.body.insertAdjacentHTML("beforeend", modalHtml);
    myModal = new bootstrap.Modal(document.getElementById("challengeModal"), {
      keyboard: false,
      backdrop: "static",
    });
    setupButtonChallengeReceived(challengerId);
  }

  myModal.show();
}

function setupButtonChallengeReceived(challengerId) {
  recreateButton("acceptChallenge");
  recreateButton("declineChallenge");

  const acceptButton = document.getElementById("acceptChallenge");
  const declineButton = document.getElementById("declineChallenge");

  acceptButton.onclick = function () {
    console.log("Challenge accepted");
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
    console.log("Challenge declined");
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

function handleChallengeResponse(data) {

  updateModalChallengeResponse(data);

  if (data.response === "accept" && data.room_url) {
    console.log("Challenge accepted");
    const url_room = data.room_url;
    console.log("Redirection vers la page de jeu, url:", url_room);
    router(url_room);
  } else {
    console.log("Challenge declined");
  }
}

function updateModalChallengeResponse(data) {
  const modal = document.getElementById("challengeModalWaiting");
  if (!modal) {
    return;
  }
  const response = data.response;

  const modalTitle = document.querySelector(
    "#challengeModalWaiting .modal-title"
  );

  const modalBody = document.querySelector(
    "#challengeModalWaiting .modal-body"
  );

  if (modalTitle)
    modalTitle.textContent =
      response === "accept" ? "Défi accepté!" : "Défi refusé";
  if (modalBody)
    modalBody.innerHTML = `<p>${response === "accept" ? "Préparation du jeu..." : "L'adversaire a refusé le défi."}</p>`;

  const cancelButton = document.getElementById("cancelWaiting");
  if (cancelButton) cancelButton.remove();

  setTimeout(() => {
    const waitingModalElement = document.getElementById(
      "challengeModalWaiting"
    );
    const waitingModal = bootstrap.Modal.getInstance(waitingModalElement);
    if (response === "accept") {
      console.log("Redirection vers la page de jeu");
      if (waitingModal) {
        waitingModal.hide();
        waitingModalElement.remove();
      }
    } else {
      if (waitingModal) {
        waitingModal.hide();
        waitingModalElement.remove();
      }
    }
  }, 3000);
}

function hamdleChallengeError(data) {
  updateModalChallengeError(data);
}

function updateModalChallengeError(data) {
  const modal = document.getElementById("challengeModalWaiting");
  if (!modal) {
    return;
  }

  const modalTitle = document.querySelector(
    "#challengeModalWaiting .modal-title"
  );

  const modalBody = document.querySelector(
    "#challengeModalWaiting .modal-body"
  );

  if (modalTitle) modalTitle.textContent = "Erreur";
  if (modalBody) modalBody.innerHTML = `<p>${data.message}</p>`;

  const cancelButton = document.getElementById("cancelWaiting");
  if (cancelButton) cancelButton.remove();

  setTimeout(() => {
    const waitingModalElement = document.getElementById(
      "challengeModalWaiting"
    );
    const waitingModal = bootstrap.Modal.getInstance(waitingModalElement);
    if (waitingModal) {
      waitingModal.hide();
      waitingModalElement.remove();
    }
  }, 3000);
}

function handleChallengeCanceled(data) {
  updateModalChallengeCanceled(data);
}

function updateModalChallengeCanceled(data) {
  const modal = document.getElementById("challengeModal");
  if (!modal) {
    return;
  }

  const modalTitle = document.querySelector("#challengeModal .modal-title");
  const modalBody = document.querySelector("#challengeModal .modal-body");

  modalTitle.textContent = "Défi annulé";
  modalBody.innerHTML = `<p>L'adversaire a annulé le défi.</p>`;

  const acceptButton = document.getElementById("acceptChallenge");
  const declineButton = document.getElementById("declineChallenge");
  if (acceptButton) acceptButton.remove();
  if (declineButton) declineButton.remove();

  setTimeout(() => {
    const waitingModalElement = document.getElementById("challengeModal");
    const waitingModal = bootstrap.Modal.getInstance(waitingModalElement);
    if (waitingModal) {
      waitingModal.hide();
      waitingModalElement.remove();
    }
  }, 3000);
}
