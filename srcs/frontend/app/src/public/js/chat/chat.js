// fetchTemplate
import { fetchTemplate } from "../pageUtils.js";
import { loadProfileCss, requestDataWithToken } from "../pageUtils.js";
import { getFriendList, getProfile } from "../profile/getProfile.js";
import { router, api_url } from "../main.js";
import { sendUpdateRequest } from "../profile/profileUtils.js";

let conversations = {};
let currentFriendId;
export let chatSocket;
let senderId;
let clientSender;
let blocked_users = [];

export async function displayChatPage() {
  try {
    resetCurrentFriendId();
    clientSender = await getProfile();
    blocked_users = clientSender.blocked_users;
    senderId = clientSender.id;
    loadProfileCss("/public/css/chat.css");
    const chatTemplate = await fetchTemplate("/public/html/chat.html");
    document.getElementById("main").innerHTML = chatTemplate;
    const friends = await getFriendList();
    let friendsListIds = constructFriendsListId(friends);
    await injectFriendsInChat(friends);
    await etablishConnectionWebSocket(friendsListIds);
    await injectUsersNotFriendsInChat(friendsListIds);
    await handleSendButton();
    createConversationObjects(friends, clientSender);
    await attachSearchListenerChat(friendsListIds);
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
  if (chatSocket.readyState !== WebSocket.OPEN) {
    return;
  }
  chatSocket.send(
    JSON.stringify({
      action: "subscribe",
      usersIds: friendsListIds,
    })
  );
}

export function handleStatusUpdate(data) {
  console.log("Status update:", data);
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

export function getStatusUpdatesFromServer() {
  chatSocket.send(
    JSON.stringify({
      action: "get_status_updates",
    })
  );
}

function handleWebSocketOpen(friendsListIds, resolve) {
  console.log("Connection opened");
  subscribeToStatusUpdates(friendsListIds);
  resolve();
}

function handleWebSocketMessage(event, friendsListIds) {
  const data = JSON.parse(event.data);
  switch (data.type) {
    case "chat_message":
      processChatMessage(data, friendsListIds);
      break;
    case "status_update":
      handleStatusUpdate(data);
      break;
    default:
      console.log("Unknown message type:", data);
  }
}

async function processChatMessage(data, friendsListIds) {
  if (!isSenderFriend(data.sender, friendsListIds)) {
    await injectNewUserInChat(data.sender);
  }
  handleIncomingMessage(data);
}

function handleWebSocketClose(reject) {
  console.log("Connection closed");
  reject(new Error("Connection closed"));
}

function handleWebSocketError(error, reject) {
  console.error("WebSocket error:", error);
  reject(error);
}

export function etablishConnectionWebSocket(friendsListIds) {
  return new Promise((resolve, reject) => {
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
      getStatusUpdatesFromServer();
      resolve();
      return;
    }
    chatSocket = new WebSocket("wss://localhost/ws/chat");

    chatSocket.onopen = () => handleWebSocketOpen(friendsListIds, resolve);
    chatSocket.onmessage = (event) =>
      handleWebSocketMessage(event, friendsListIds);
    chatSocket.onclose = () => handleWebSocketClose(reject);
    chatSocket.onerror = (error) => handleWebSocketError(error, reject);
  });
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
  const userInChat = document.querySelector(`[data-uid="${uid}"]`);
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
  uid = [uid];
  subscribeToStatusUpdates(uid);
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

        const uid = link.getAttribute("data-uid");
        currentFriendId = uid;
        injectChatRoom(uid);
        injectInfoOnUserChat(uid);
      });
      link.setAttribute("data-listener-added", "true");
    }
  });
}

export async function injectInfoOnUserChat(uid) {
  const conversation = conversations[uid];
  if (!conversation) {
    return;
  }
  const userName = conversation.friend_name;
  const userAvatar = conversation.friend_avatar;
  const userUID = conversation.friend_id;

  const chatInfo = document.getElementById("info-user-chat");
  chatInfo.innerHTML = "";
  const info = document.createElement("div");
  info.classList.add("py-2", "px-4", "border-bottom");
  info.innerHTML = `
      <div class="d-flex align-items-center py-1">
          <div class="position-relative">
              <img src="${userAvatar}" class="rounded-circle me-1" alt="${userName}" width="40" height="40">
          </div>
          <div class="flex-grow-1 ps-3">
              <span class="profile-link-chat" data-uid="${userUID}"><strong>${userName}</strong></span>
          </div>
          <div class="d-flex align-items-center">
              <button id="invite-to-play-button" class="btn btn-outline-secondary btn-sm">Invite to play</button>
              <button id="add-remove-friend-chat" class="btn btn-outline-secondary btn-sm">Add friend</button>
              <button id="block-unblock-chat" class="btn btn-outline-secondary btn-sm">Block</button>
          </div>
      </div>
  `;
  chatInfo.appendChild(info);
  await attachLinkListenerProfileChat();
  await setupAddRemoveFriendButton(userUID);
  await setupBlockUnblockButton(userUID);
  await setupInviteToPlayButton(userUID);
}

export async function setupInviteToPlayButton(uid) {
  const inviteToPlayButton = document.getElementById("invite-to-play-button");
  inviteToPlayButton.addEventListener("click", async () => {
    console.log("Invite to play button clicked user = ", uid);
    // router("/play/" + uid);
  });
}

export async function checkIfBlocked(uid) {
  return blocked_users.includes(uid);
}

export async function setupBlockUnblockButton(uid) {
  const blockUnblockButton = document.getElementById("block-unblock-chat");
  const isBlocked = await checkIfBlocked(uid);
  if (isBlocked) {
    blockUnblockButton.textContent = "Unblock";
  } else {
    blockUnblockButton.textContent = "Block";
  }
  blockUnblockButton.addEventListener("click", async () => {
    if (isBlocked) {
      await unblockUser(uid);
    } else {
      await blockUser(uid);
    }
  });
}

export async function blockUser(uid) {
  try {
    const dataToUpdate = {};
    dataToUpdate["blocked_users"] = [uid];
    const updateSuccess = await sendUpdateRequest(
      api_url + "users/profile/update",
      dataToUpdate
    );
    if (updateSuccess) {
      console.log("User blocked successfully");
      await displayChatPage();
    } else {
      console.error("Error blocking user");
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

export async function unblockUser(uid) {
  try {
    const dataToUpdate = {};
    dataToUpdate["blocked_users"] = [uid];
    const updateSuccess = await sendUpdateRequest(
      api_url + "users/remove_blocked",
      dataToUpdate
    );
    if (updateSuccess) {
      console.log("User unblocked successfully");
      await displayChatPage();
    } else {
      console.error("Error unblocking user");
    }
  } catch (error) {
    console.error("Error:", error);
  }
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

export async function checkIfFriend(uid) {
  const friends = await getFriendList(0);
  return friends.results.some((friend) => friend.id === uid);
}

export async function addFriend(uid) {
  try {
    const dataToUpdate = {};
    dataToUpdate["friends"] = [uid];
    const updateSuccess = await sendUpdateRequest(
      api_url + "users/profile/update",
      dataToUpdate
    );
    if (updateSuccess) {
      console.log("Friend added successfully");
      await displayChatPage();
    } else {
      console.error("Error adding friend");
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

export async function removeFriend(uid) {
  try {
    const dataToUpdate = {};
    dataToUpdate["friends"] = [uid];
    const updateSuccess = await sendUpdateRequest(
      api_url + "users/remove_friends",
      dataToUpdate
    );
    if (updateSuccess) {
      console.log("Friend removed successfully");
      await displayChatPage();
    } else {
      console.error("Error removing friend");
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

export async function setupAddRemoveFriendButton(uid) {
  try {
    const addRemoveButton = document.getElementById("add-remove-friend-chat");
    const isFriend = await checkIfFriend(uid);
    if (isFriend) {
      addRemoveButton.textContent = "Remove friend";
    } else {
      addRemoveButton.textContent = "Add friend";
    }
    addRemoveButton.addEventListener("click", async () => {
      if (isFriend) {
        await removeFriend(uid);
      } else {
        await addFriend(uid);
      }
    });
  } catch (error) {
    console.error("Error:", error);
  }
}
