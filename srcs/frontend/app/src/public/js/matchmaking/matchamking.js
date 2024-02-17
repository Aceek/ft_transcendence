import { api_url, router } from "../main.js";
import { loadScript, fetchTemplate, loadProfileCss } from "../pageUtils.js";

export async function displayMatchmaking() {
  try {
    const matchmakingHtml = await fetchTemplate(
      "/public/html/matchmaking.html"
    );
    document.getElementById("main").innerHTML = matchmakingHtml;
    await addEventListenerForMatchmakingButton();
  } catch (error) {
    console.error("Error:", error);
    router("/home");
  }
}

async function addEventListenerForMatchmakingButton() {
  const matchmakingButton = document.getElementById("matchmakingButton");
  matchmakingButton.addEventListener("click", async () => {
    console.log("Matchmaking button clicked");
    await initiateMatchmaking();
  });
}

async function initiateMatchmaking() {
  const ws = new WebSocket(`wss://${window.location.host}/ws/matchmaking/`);
  ws.onopen = () => {
    console.log("WebSocket connected");
    ws.send(JSON.stringify({ message: "Hello from client" }));
  };

  ws.onmessage = function (event) {
    const data = JSON.parse(event.data);
    if (data.message === "Match found") {
      if (data.room_url) {
        router(data.room_url);
      }
    }
  };

  ws.onclose = () => {
    console.log("WebSocket closed");
  };

  ws.onerror = (error) => {
    console.error("WebSocket error:", error);
  };
}
