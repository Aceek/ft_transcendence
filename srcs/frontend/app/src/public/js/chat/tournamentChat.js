import { incressBadgeBgSuccess } from "./utilsChat.js";
import { conversations, currentFriendId } from "./chat.js";
import { resetCurrentFriendId, setCurrentFriendId } from "./chat.js";
import { injectChatRoom } from "./injectChat.js";
import { router } from "../main.js";

export async function handleTournamentMessage(data) {
  const { message, tournamentId } = data;

  createConversationsTournament();
  conversations["tournament-bot"].messages.push({
    text: message,
    tournamentId: tournamentId,
  });
  if (currentFriendId === "tournament-bot") {
    injectChatRoom("tournament-bot", false, createTournamentMessage);
    attashLinkListenerTournamentChat();
  } else {
    incressBadgeBgSuccess("tournament-bot");
  }
}

export async function attashLinkListenerTournamentChat() {
  const tournamentLinks = document.querySelectorAll(".tournament-link-chat");
  tournamentLinks.forEach((link) => {
    if (!link.getAttribute("data-listener-added")) {
      link.addEventListener("click", async (event) => {
        const tournamentId = link.getAttribute("data-uid");
        router("/tournament/" + tournamentId);
      });
      link.setAttribute("data-listener-added", "true");
    }
  });
}

export function createTournamentMessage(message) {
  const messageElement = document.createElement("div");
  messageElement.classList.add("chat-message-left");
  messageElement.classList.add("pb-4");

  messageElement.innerHTML = `
    <div class="d-flex align-items-center">
      <img src="/public/images/profile.jpg" class="rounded-circle me-1" alt="tournament-avatar" width="40" height="40">
    </div>
    <div id="left-background" class="flex-shrink-1 bg-light rounded py-2 px-3 mr-3">
      <div class="font-weight-bold mb-1">Tournament info</div>
      <div class="message-content tournament-link-chat" data-uid=${message.tournamentId}>${message.text}</div>
    </div>
  `;
  return messageElement;
}

export function createConversationsTournament() {
  if (!conversations["tournament-bot"]) {
    conversations["tournament-bot"] = {
      messages: [],
    };
  }
}

export function manageTournamentBot() {
  setCurrentFriendId("tournament-bot");
  injectChatRoom("tournament-bot", false, createTournamentMessage);
  attashLinkListenerTournamentChat();
  resetInfoOnUserChat();
}

export function resetInfoOnUserChat() {
  const chatMessages = document.getElementById("info-user-chat");
  if (chatMessages) {
    chatMessages.innerHTML = "";
  }
}

export function clearTournamentConversationsMessages() {
  if (conversations["tournament-bot"]) {
    conversations["tournament-bot"].messages = [];
  }
}
