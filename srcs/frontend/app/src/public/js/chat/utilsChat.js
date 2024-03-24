import {
  conversations,
  blocked_users,
  displayChatPage,
  senderId,
  clientSender,
} from "./chat.js";
import { injectNewUserInChat } from "./injectChat.js";
import { handleIncomingMessage } from "./websocketChat.js";
import { sendUpdateRequest } from "../profile/profileUtils.js";
import { getFriendList } from "../profile/getProfile.js";
import { api_url, router } from "../main.js";
import { handleSendChallenge } from "../user_activity_websocket/user_activity_handle.js";


export async function displaySearchResults(users, container, friendsListIds) {
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

export function constructFriendsListId(friends) {
  const friendsListIds = [];
  friends.results.forEach((friend) => {
    friendsListIds.push(friend.id);
  });
  return friendsListIds;
}

export function createConversationObjects(friends, clientSender) {
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


function isSenderFriend(sender, friendsListIds) {
  return friendsListIds.includes(sender);
}

function isConversationOpen(senderUID) {
  return conversations[senderUID] !== undefined;
}

export async function processChatMessage(data, friendsListIds) {
  if (
    !isSenderFriend(data.sender, friendsListIds) &&
    !isConversationOpen(data.sender)
  ) {
    await injectNewUserInChat(data.sender);
  }
  handleIncomingMessage(data);
}

export function incressBadgeBgSuccess(uid) {
  const friendLink = document.querySelector(`[data-uid="${uid}"]`);
  if (!friendLink) {
    return;
  }
  const badge = friendLink.querySelector(".badge");
  badge.classList.remove("bg-secondary");
  badge.classList.add("bg-success");

  badge.textContent = parseInt(badge.textContent) + 1;
}

export function scrollToBottom() {
  const chatMessages = document.querySelector(".chat-messages");
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

export function createMessageElement(message, conversation) {
  const messageElement = document.createElement("div");
  const isSender = message.sender === senderId;
  messageElement.classList.add(isSender ? "chat-message-right" : "chat-message-left");
  messageElement.classList.add("pb-4");

  const senderName = isSender ? conversation.client_name : conversation.friend_name;
  const avatar = isSender ? conversation.client_avatar : conversation.friend_avatar;

  // Create elements for the message
  const avatarElement = document.createElement("img");
  avatarElement.src = avatar;
  avatarElement.alt = senderName;
  avatarElement.classList.add("rounded-circle", "me-1");
  avatarElement.width = 40;
  avatarElement.height = 40;

  const timeElement = document.createElement("div");
  timeElement.classList.add("text-muted", "small", "text-nowrap", "mt-2");
  timeElement.textContent = message.time || "2:34 am";

  const nameElement = document.createElement("div");
  nameElement.classList.add("font-weight-bold", "mb-1");
  nameElement.textContent = senderName;

  const messageContent = document.createElement("div");
  messageContent.classList.add("message-content");
  messageContent.textContent = message.text;

  // Construct the message element
  const flexContainer = document.createElement("div");
  flexContainer.style.display = "flex";
  flexContainer.style.flexDirection = "column";
  flexContainer.style.alignItems = "center";
  if (isSender) {
    flexContainer.style.marginLeft = "5px";
  } else {
    flexContainer.style.marginRight = "5px";
  }

  flexContainer.appendChild(avatarElement);
  flexContainer.appendChild(timeElement);

  const backgroundDiv = document.createElement("div");
  backgroundDiv.id = isSender ? "right-background" : "left-background";
  backgroundDiv.classList.add("flex-shrink-1", "bg-dark", "rounded", "py-2", "px-3");
  if (isSender) {
    backgroundDiv.classList.add("ml-3");
  } else {
    backgroundDiv.classList.add("mr-3");
  }

  backgroundDiv.appendChild(nameElement);
  backgroundDiv.appendChild(messageContent);

  messageElement.appendChild(flexContainer);
  messageElement.appendChild(backgroundDiv);

  return messageElement;
}

export function resetBadgeBgSuccess(uid) {
  const friendLink = document.querySelector(`[data-uid="${uid}"]`);
  if (!friendLink) {
    return;
  }
  const badge = friendLink.querySelector(".badge");
  badge.classList.remove("bg-success");
  badge.classList.add("bg-secondary");

  badge.textContent = "0";
}

export async function setupInviteToPlayButton(uid) {
  const inviteToPlayButton = document.getElementById("invite-to-play-button");
  inviteToPlayButton.addEventListener("click", async () => {
    await handleSendChallenge(uid);
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
    if (updateSuccess.success) {
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
    if (updateSuccess.success) {
      await displayChatPage();
    } else {
      console.error("Error unblocking user");
    }
  } catch (error) {
    console.error("Error:", error);
  }
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
    if (updateSuccess.success) {
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
    if (updateSuccess.success) {
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
