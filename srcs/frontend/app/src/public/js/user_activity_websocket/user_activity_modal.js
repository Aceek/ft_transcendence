import { connectUserActivitySocket } from "./user_activity_websocket.js";
import { userActivitySocket } from "./user_activity_websocket.js";

export async function handleUserActivity() {
  if (
    userActivitySocket === null ||
    userActivitySocket.readyState === WebSocket.CLOSED
  ) {
    connectUserActivitySocket();
  }
}

export async function updateModalChallengeNoResponse() {
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

export function updateModalChallengeResponse(data) {
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

export function updateModalChallengeError(data) {
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

export function updateModalChallengeCanceled(data) {
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
