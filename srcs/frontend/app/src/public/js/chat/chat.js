// fetchTemplate
import { fetchTemplate } from "../pageUtils.js";
import { loadProfileCss, requestDataWithToken } from "../pageUtils.js";
import { getFriendList, getProfile } from "../profile/getProfile.js";
import { router, api_url } from "../main.js";

let conversations = {};
let currentFriendId;
export let chatSocket;
let senderId;
let clientSender;

export async function displayChatPage() {
  try {
    clientSender = await getProfile();
    senderId = clientSender.id;
    loadProfileCss("/public/css/chat.css");
    const chatTemplate = await fetchTemplate("/public/html/chat.html");
    document.getElementById("main").innerHTML = chatTemplate;
    const friends = await getFriendList();
    const friendsListIds = constructFriendsListId(friends);
    await injectFriendsInChat(friends);
    await injectUsersNotFriendsInChat(friendsListIds);
    await handleSendButton();
    createConversationObjects(friends, clientSender);
    await attachSearchListenerChat(friendsListIds);
    await etablishConnectionWebSocket(friendsListIds);
  } catch (error) {
    console.error("Error:", error);
    // router("/home");
  }
}

async function attachSearchListenerChat(friendsListIds) {
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

async function displaySearchResults(users, container, friendsListIds) {
  users.forEach((user) => {
    if (friendsListIds.includes(user.id) || user.id === senderId) {
      return;
    }
    const userElement = document.createElement("div");
    userElement.className = "search-result-item";
    userElement.textContent = user.username;
    userElement.addEventListener("click", async () => {
      createConversationSingleUser(user);
      await injectNewUserInChat(user.id);
      console.log(`User ${user.username} clicked!`);
    });
    container.appendChild(userElement);
  });
}

async function createConversationSingleUser(user) {
  conversations[user.id] = {
    messages: [],
    friend_id: user.id,
    friend_name: user.username,
    friend_avatar: user.avatar || "/public/images/profile.jpg",
    client_id: clientSender.id,
    client_name: clientSender.username,
    client_avatar: clientSender.avatar || "/public/images/profile.jpg",
  };
}

export async function injectUsersNotFriendsInChat(friendsListIds) {
  for (const uid in conversations) {
    if (!friendsListIds.includes(uid)) {
      await injectNewUserInChat(uid);
    }
  }
}

export function resetCurrentFriendId() {
  currentFriendId = null;
}

function constructFriendsListId(friends) {
  const friendsListIds = [];
  friends.results.forEach((friend) => {
    friendsListIds.push(friend.id);
  });
  return friendsListIds;
}

function createConversationObjects(friends, clientSender) {
  friends.results.forEach((friend) => {
    conversations[friend.id] = {
      messages: [],
      friend_id: friend.id,
      friend_name: friend.username,
      friend_avatar: friend.avatar || "/public/images/profile.jpg",
      client_id: clientSender.id,
      client_name: clientSender.username,
      client_avatar: clientSender.avatar || "/public/images/profile.jpg",
    };
  });
}

export async function handleSendButton() {
  const sendButton = document.getElementById("send-message-button");
  const messageInput = document.getElementById("message-input");

  const sendMessage = async () => {
    const message = messageInput.value;
    if (currentFriendId === undefined || currentFriendId === null) {
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
      action: "send_message",
      message: message.text,
      receiver: message.receiver,
      sender: message.sender,
      time: message.time,
    });

    chatSocket.send(messageData);
    return true;
  } else {
    console.log("WebSocket is not open. Cannot send message.");
    return false;
  }
}

export function subscribeToStatusUpdates(friendsListIds) {
  chatSocket.send(
    JSON.stringify({
      action: "subscribe",
      usersIds: friendsListIds,
    })
  );
}

export function handleStatusUpdate(data) {
  const { user_id, status } = data;
  const friendLink = document.querySelector(`[data-uid="${user_id}"]`);
  if (friendLink) {
    const statusElement = friendLink.querySelector(".connection-status");
    if (status === "online") {
      statusElement.classList.add("text-online");
      statusElement.classList.remove("text-offline");
      statusElement.textContent = "Chat online";
    } else {
      statusElement.classList.add("text-offline");
      statusElement.classList.remove("text-online");
      statusElement.textContent = "Chat offline";
    }
  }
}

function isSenderFriend(sender, friendsListIds) {
  return friendsListIds.includes(sender);
}

export async function etablishConnectionWebSocket(friendsListIds) {
  if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
    return;
  }
  chatSocket = new WebSocket("wss://localhost/ws/chat");
  chatSocket.onopen = function () {
    console.log("Connection opened");
    subscribeToStatusUpdates(friendsListIds);
  };
  chatSocket.onmessage = async function (event) {
    const data = JSON.parse(event.data);
    if (data.type && data.type === "chat_message") {
      if (!isSenderFriend(data.sender, friendsListIds)) {
        await injectNewUserInChat(data.sender);
      }
      handleIncomingMessage(data);
    } else if (data.type && data.type === "status_update") {
      handleStatusUpdate(data);
    } else {
      console.log("Unknown message type:", data);
    }
  };
  chatSocket.onclose = function () {
    console.log("Connection closed");
  };
  chatSocket.onerror = function (error) {
    console.error("Error:", error);
  };
}

export async function handleIncomingMessage(data) {
  const { sender, message, receiver, time } = data;
  if (!conversations[sender]) {
    const newUsers = await getProfile(sender);
    conversations[sender] = {
      messages: [],
      friend_id: newUsers.id,
      friend_name: newUsers.username,
      friend_avatar: newUsers.avatar || "/public/images/profile.jpg",
      client_id: clientSender.id,
      client_name: clientSender.username,
      client_avatar: clientSender.avatar || "/public/images/profile.jpg",
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
  } else {
    incressBadgeBgSuccess(sender);
  }
}

export async function injectNewUserInChat(uid) {
  const userInChat = document.querySelector(`li[data-uid="${uid}"]`);
  if (userInChat) {
    return;
  }

  const newUser = await getProfile(uid);
  const friendsInChat = document.getElementById("users_in_chat");

  let notFriendTitle = document.getElementById("not-friends-title");
  if (!notFriendTitle) {
    notFriendTitle = document.createElement("h5");
    notFriendTitle.id = "not-friends-title";
    notFriendTitle.textContent = "Not Friends";
    friendsInChat.appendChild(notFriendTitle);
  }

  const listItem = document.createElement("li");
  listItem.setAttribute("data-uid", newUser.id);
  listItem.innerHTML = `
  <a class="chat-link list-group-item list-group-item-action border-0 d-flex justify-content-between align-items-center" data-uid="${newUser.id}">
    <div class="d-flex align-items-center">
          <img src="${newUser.avatar || "/public/images/profile.jpg"}" class="rounded-circle me-2" alt="${newUser.username}" width="40" height="40">
          <div>
              ${newUser.username}
              <div class="small"><span class="connection-status text-online">Unknown</span></div>
          </div>
      </div>
      <div class="badge bg-secondary">0</div>
  </a>
  `;

  friendsInChat.appendChild(listItem);
  await attachLinkListenerChat();
}

function incressBadgeBgSuccess(uid) {
  const friendLink = document.querySelector(`[data-uid="${uid}"]`);
  if (!friendLink) {
    return;
  }
  const badge = friendLink.querySelector(".badge");
  badge.classList.remove("bg-secondary");
  badge.classList.add("bg-success");

  badge.textContent = parseInt(badge.textContent) + 1;
}

export async function injectFriendsInChat(friends) {
  const friendsInChat = document.getElementById("friends_in_chat");
  friendsInChat.innerHTML = "";
  const friendTitle = document.createElement("h5");
  friendTitle.textContent = "Friends";
  friendsInChat.appendChild(friendTitle);

  friends.results.forEach((friend) => {
    const listItem = document.createElement("li");

    listItem.innerHTML = `
    <a class="chat-link list-group-item list-group-item-action border-0 d-flex justify-content-between align-items-center" data-uid="${friend.id}">
        <div class="d-flex align-items-center">
            <img src="${friend.avatar || "/public/images/profile.jpg"}" class="rounded-circle me-2" alt="${friend.username}" width="40" height="40">
            <div>
                ${friend.username}
                <div class="small"><span class="connection-status text-online">Unknow</span></div>

            </div>
        </div>
        <div class="badge bg-secondary">0</div>
    </a>
`;

    friendsInChat.appendChild(listItem);
  });
  await attachLinkListenerChat();
}

function scrollToBottom() {
  const chatMessages = document.querySelector(".chat-messages");
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function createMessageElement(message, conversation) {
  const messageElement = document.createElement("div");
  const isSender = message.sender === senderId;
  messageElement.classList.add(
    isSender ? "chat-message-right" : "chat-message-left"
  );
  messageElement.classList.add("pb-4");

  const senderName = isSender
    ? conversation.client_name
    : conversation.friend_name;
  const avatar = isSender
    ? conversation.client_avatar
    : conversation.friend_avatar;

  messageElement.innerHTML = `
      <div style="display: flex; flex-direction: column; align-items: center; ${isSender ? "margin-left: 5px;" : "margin-right: 5px;"}">
          <img src="${avatar}" class="rounded-circle me-1" alt="${senderName}" width="40" height="40">
          <div class="text-muted small text-nowrap mt-2">${message.time || "2:34 am"}</div>
      </div>
      <div id=${isSender ? "right-background" : "left-background"} class="flex-shrink-1 bg-light rounded py-2 px-3 ${isSender ? "ml-3" : "mr-3"}">
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
    const messageElement = createMessageElement(message, conversation);
    chatMessages.appendChild(messageElement);
  });
  scrollToBottom();
  resetBadgeBgSuccess(uid);
}

function resetBadgeBgSuccess(uid) {
  const friendLink = document.querySelector(`[data-uid="${uid}"]`);
  if (!friendLink) {
    return;
  }
  const badge = friendLink.querySelector(".badge");
  badge.classList.remove("bg-success");
  badge.classList.add("bg-secondary");

  badge.textContent = "0";
}

export async function attachLinkListenerChat() {
  const chatLinks = document.querySelectorAll(".chat-link");
  chatLinks.forEach((link) => {
    if (!link.getAttribute("data-listener-added")) {
      link.addEventListener("click", async (event) => {
        const chatLinks = document.querySelectorAll(".chat-link");
        chatLinks.forEach((link) => link.classList.remove("selected"));

        event.currentTarget.classList.add("selected");
        console.log("Chat link clicked:", link);

        const uid = link.getAttribute("data-uid");
        currentFriendId = uid;
        injectChatRoom(uid);
      });
      link.setAttribute("data-listener-added", "true");
    }
  });
}
