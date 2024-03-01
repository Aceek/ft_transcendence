import { currentFriendId, senderId, setCurrentFriendId } from "./chat.js";
import { injectChatRoom, injectInfoOnUserChat } from "./injectChat.js";
import { router, api_url } from "../main.js";
import { displaySearchResults } from "./utilsChat.js";
import { sendMessageWebSocket } from "./websocketChat.js";
import { handleOutgoingMessage } from "./websocketChat.js";
import { requestDataWithToken } from "../pageUtils.js";
import { manageTournamentBot } from "./tournamentChat.js";

export async function attachLinkListenerChat() {
  const chatLinks = document.querySelectorAll(".chat-link");
  chatLinks.forEach((link) => {
    if (!link.getAttribute("data-listener-added")) {
      link.addEventListener("click", async (event) => {
        const chatLinks = document.querySelectorAll(".chat-link");
        chatLinks.forEach((link) => link.classList.remove("selected"));

        event.currentTarget.classList.add("selected");

        const uid = link.getAttribute("data-uid");
        if (uid !== "tournament-bot") {
          setCurrentFriendId(uid);
          injectChatRoom(uid);
          injectInfoOnUserChat(uid);
        } else {
          manageTournamentBot();
        }
      });
      link.setAttribute("data-listener-added", "true");
    }
  });
}

export async function attachLinkListenerProfileChat() {
  const profileLinks = document.querySelectorAll(".profile-link-chat");
  profileLinks.forEach((link) => {
    if (!link.getAttribute("data-listener-added")) {
      link.addEventListener("click", () => {
        const uid = link.getAttribute("data-uid");
        router("/profile/" + uid);
      });
      link.setAttribute("data-listener-added", "true");
    }
  });
}

export async function attachSearchListenerChat(friendsListIds) {
  const searchFriends = document.getElementById("search-bar-chat");
  const searchResultsContainer = document.createElement("div");
  searchResultsContainer.id = "search-results-container";
  searchFriends.parentNode.insertBefore(
    searchResultsContainer,
    searchFriends.nextSibling
  );

  searchFriends.addEventListener("input", async () => {
    const searchValue = searchFriends.value.trim();
    searchResultsContainer.innerHTML = "";
    if (searchValue.length > 0) {
      try {
        let usersInSearch = await requestDataWithToken(
          `${api_url}users?search=${searchValue}`,
          null,
          "GET"
        );
        usersInSearch = await usersInSearch.json();
        await displaySearchResults(
          usersInSearch,
          searchResultsContainer,
          friendsListIds
        );
      } catch (error) {
        console.error("Error:", error);
      }
    }
  });
}

export async function handleSendButton() {
  const sendButton = document.getElementById("send-message-button");
  const messageInput = document.getElementById("message-input");

  const sendMessage = async () => {
    const message = messageInput.value;
    if (
      currentFriendId === undefined ||
      currentFriendId === null ||
      currentFriendId === "tournament-bot"
    ) {
      return;
    }
    if (message) {
      const data = {
        sender: senderId,
        text: message,
        receiver: currentFriendId,
        time: new Date().toLocaleTimeString(),
      };
      if (sendMessageWebSocket(data)) {
        handleOutgoingMessage(data);
      }
      messageInput.value = "";
    }
  };

  sendButton.addEventListener("click", async () => {
    await sendMessage();
  });

  messageInput.addEventListener("keydown", async (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      await sendMessage();
    }
  });
}
