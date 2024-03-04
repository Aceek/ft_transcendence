import { api_url, router } from "../main.js";
import { loadScript, fetchTemplate, loadProfileCss } from "../pageUtils.js";

let ws;

export async function handleMatchmaking(numberOfPlayers) {
  await injectModalMatchmaking();
  initiateMatchmaking(numberOfPlayers);
}

async function injectModalMatchmaking() {
  let myModal = bootstrap.Modal.getInstance(
    document.getElementById("matchmakingModal")
  );

  if (!myModal) {
    const modalHtml = await fetchTemplate(
      "/public/html/popup-matchmaking.html"
    );
    document.body.insertAdjacentHTML("beforeend", modalHtml);
    myModal = new bootstrap.Modal(document.getElementById("matchmakingModal"), {
      keyboard: false,
      backdrop: "static",
    });

    document
      .getElementById("cancelMatchmaking")
      .addEventListener("click", function () {
        console.log("Annulation du matchmaking par l'utilisateur.");
        ws.send(JSON.stringify({ action: "cancelMatchmaking" }));
        ws.close();

        var myModal = bootstrap.Modal.getInstance(
          document.getElementById("matchmakingModal")
        );
        if (myModal) {
          myModal.hide();
        }
      });
  }

  myModal.show();
}

async function initiateMatchmaking(numberOfPlayers) {
  ws = new WebSocket(`wss://${window.location.host}/ws/matchmaking/`);
  ws.onopen = () => {
    console.log("WebSocket connected");
    ws.send(
      JSON.stringify({
        action: "startMatchmaking",
        mode: numberOfPlayers,
      })
    );
  };

  ws.onmessage = function (event) {
    const data = JSON.parse(event.data);
    if (data.error) {
      console.log("Message from server: ", data.message);
      printMessageFromServerInNavbar(data.message);
    } else if (data.message === "Match found") {
      closeModal();
      ws.close();
      if (data.room_url) {
        console.log("Match found, redirecting to room:", data.room_url);
        router(data.room_url);
      }
    } else {
      console.log("Message from server: ", data.message);
    }
  };

  ws.onclose = () => {
    console.log("WebSocket closed");
    closeModal();
  };
  ws.onerror = (error) => {
    console.error("WebSocket error:", error);
    closeModal();
  };
}

function printMessageFromServerInNavbar(message) {
  const navbar = document.getElementById("navbar");
  const alert = document.createElement("div");
  alert.classList.add(
    "alert",
    "alert-warning",
    "alert-dismissible",
    "fade",
    "show"
  );
  alert.setAttribute("role", "alert");
  alert.innerHTML = `
    <strong>Attention!</strong> ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  navbar.appendChild(alert);
  setTimeout(() => {
    alert.remove();
  }, 3000);
}

function closeModal() {
  var myModal = bootstrap.Modal.getInstance(
    document.getElementById("matchmakingModal")
  );
  if (myModal) {
    myModal.hide();
  }
}
