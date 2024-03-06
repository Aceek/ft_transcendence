import { attachLinkListenerChat } from "./attashListenerChat.js";
import { createMessageElement } from "./utilsChat.js";
import { scrollToBottom } from "./utilsChat.js";
import { resetBadgeBgSuccess } from "./utilsChat.js";
import { sendReadStatus } from "./websocketChat.js";
import { attachLinkListenerProfileChat } from "./attashListenerChat.js";
import {
  setupAddRemoveFriendButton,
  setupBlockUnblockButton,
  setupInviteToPlayButton,
} from "./utilsChat.js";
import { getProfile } from "../profile/getProfile.js";
import { conversations } from "./chat.js";
import { sendTrackStatus } from "../user_activity_websocket/user_activity_utils.js";

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
                <span id="status-${friend.id}" class=${friend.status === "online" ? "text-success" : "text-danger"}>• ${friend.status}</span>
            </div>
        </div>
        <div class="badge bg-secondary">0</div>
    </a>
`;

    friendsInChat.appendChild(listItem);
  });
  sendTrackStatus(friends.results.map((friend) => friend.id));
  await attachLinkListenerChat();
}

export async function injectUsersNotFriendsInChat(friendsListIds) {
  for (const uid in conversations) {
    if (!friendsListIds.includes(uid)) {
      await injectNewUserInChat(uid);

    }
  }
}

export function injectChatRoom(
  uid,
  readStatus = true,
  createElementfunction = createMessageElement
) {
  const chatMessages = document.getElementById("chat-messages-div");
  chatMessages.innerHTML = "";

  const conversation = conversations[uid];
  if (!conversation) {
    return;
  }
  const messages = conversation.messages || [];

  messages.forEach((message) => {
    const messageElement = createElementfunction(message, conversation);
    chatMessages.appendChild(messageElement);
  });
  scrollToBottom();
  resetBadgeBgSuccess(uid);
  if (readStatus) {
    sendReadStatus(uid);
  }
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
              <span id="status-${newUser.id}" class=${newUser.status === "online" ? "text-success" : "text-danger"}>• ${newUser.status}</span>
          </div>
      </div>
      <div class="badge bg-secondary">0</div>
  </a>
  `;

  friendsInChat.appendChild(listItem);
  await attachLinkListenerChat();
  sendTrackStatus([uid]);
}
