import { setupButtonChallengeReceived } from "./user_activity_utils.js";
import { fetchTemplate } from "../pageUtils.js";
import { userActivitySocket } from "./user_activity_websocket.js";

export async function injectModalChallengeWaiting(uid) {
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
      userActivitySocket.send(
        JSON.stringify({ action: "cancel_challenge", challenged_id: uid })
      );
      myModal.hide();
    });

  myModal.show();
}

export async function injectModalChallengeReceived(challengerId) {
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
