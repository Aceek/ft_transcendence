// fetchTemplate
import { fetchTemplate } from "../pageUtils.js";
import { loadProfileCss } from "../pageUtils.js";
import { getFriendList, getProfile } from "../profile/getProfile.js";
import { router } from "../main.js";

let conversations = {};
let currentFriendId;
let chatSocket;
let senderId;

export async function displayChatPage() {
  try {
    senderId = (await getProfile()).id;
    loadProfileCss("/public/css/chat.css");
    const chatTemplate = await fetchTemplate("/public/html/chat.html");
    document.getElementById("main").innerHTML = chatTemplate;
    etablishConnectionWebSocket();
    const friends = await getFriendList();
    await injectFriendsInChat(friends);
    await handleSendButton();
  } catch (error) {
    console.error("Error:", error);
    // router("/home");
  }
}

export async function handleSendButton() {
  const sendButton = document.getElementById("send-message-button");
  const messageInput = document.getElementById("message-input");

  const sendMessage = async () => {
    const message = messageInput.value;
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

function handleOutgoingMessage(data) {
  const { sender, text, receiver, time } = data;
  if (!conversations[receiver]) {
    conversations[receiver] = {
      messages: [],
    };
  }
  conversations[receiver].messages.push({
    text,
    receiver,
    sender,
    time,
  });
  if (currentFriendId === receiver) {
    injectChatRoom(receiver);
  }
}

export function sendMessageWebSocket(message) {
  if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
    const messageData = JSON.stringify({
      // Formattez votre message comme requis par le backend
      action: "send_message",
      message: message.text,
      receiver: message.receiver,
      sender: message.sender,
      time: message.time,
    });
    console.log("Sending message:", messageData);

    chatSocket.send(messageData);
    return true;
  } else {
    console.log("WebSocket is not open. Cannot send message.");
    return false;
    // Vous pourriez vouloir gérer la reconnexion ici
  }
}

export function etablishConnectionWebSocket() {
  chatSocket = new WebSocket("wss://localhost/ws/chat");
  chatSocket.onopen = function () {
    console.log("Connection opened");
  };
  chatSocket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    handleIncomingMessage(data);
  };
  chatSocket.onclose = function () {
    console.log("Connection closed");
  };
  chatSocket.onerror = function (error) {
    console.error("Error:", error);
  };
}

export function handleIncomingMessage(data) {
  const { sender, message, receiver, time } = data;
  if (!conversations[sender]) {
    conversations[sender] = {
      messages: [],
    };
  }
  conversations[sender].messages.push({
    text: message,
    receiver,
    sender,
    time,
  });
  if (currentFriendId === sender) {
    injectChatRoom(sender);
  }
}

export async function injectFriendsInChat(friends) {
  const friendsInChat = document.getElementById("friends_in_chat");
  friendsInChat.innerHTML = "";

  friends.results.forEach((friend) => {
    const listItem = document.createElement("li");

    listItem.innerHTML = `
    <a class="chat-link list-group-item list-group-item-action border-0 d-flex justify-content-between align-items-center" data-uid="${friend.id}">
        <div class="d-flex align-items-center">
            <img src="${friend.avatar || "/public/images/profile.jpg"}" class="rounded-circle me-2" alt="${friend.username}" width="40" height="40">
            <div>
                ${friend.username}
                <div class="small"><span class="text-online">Online</span></div>

            </div>
        </div>
        <div class="badge bg-success">5</div>
    </a>
`;

    friendsInChat.appendChild(listItem);
  });
  await attachLinkListenerChat();
}

function createMessageElement(message) {
  const messageElement = document.createElement("div");
  const isSender = message.sender === senderId;
  messageElement.classList.add(
    isSender ? "chat-message-right" : "chat-message-left"
  );
  messageElement.classList.add("pb-4");
  const senderName = message.sender;
  messageElement.innerHTML = `
      <div>
          <span class="text-muted small">${message.sender}</span>
          <div class="text-muted small text-nowrap mt-2">${message.time || "2:34 am"}</div>
      </div>
      <div id=${isSender ? "right-background" : "left-background"} class="flex-shrink-1 bg-light rounded py-2 px-3 ml-3">
          <div class="font-weight-bold mb-1">${senderName}</div>
          <div class="message-content">${message.text}</div>
      </div>
  `;
  return messageElement;
}

function injectChatRoom(uid) {
  const chatMessages = document.getElementById("chat-messages-div");
  chatMessages.innerHTML = "";

  const conversation = conversations[uid];
  if (!conversation) {
    return;
  }
  const messages = conversation.messages || [];

  messages.forEach((message) => {
    const messageElement = createMessageElement(message);
    chatMessages.appendChild(messageElement);
  });
}

export async function attachLinkListenerChat() {
  const chatLinks = document.querySelectorAll(".chat-link");
  chatLinks.forEach((link) => {
    if (!link.getAttribute("data-listener-added")) {
      link.addEventListener("click", async () => {
        const uid = link.getAttribute("data-uid");
        currentFriendId = uid;
        injectChatRoom(uid);
      });
      link.setAttribute("data-listener-added", "true");
    }
  });
}
