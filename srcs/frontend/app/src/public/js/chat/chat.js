import { fetchTemplate } from "../pageUtils.js";
import { loadProfileCss } from "../pageUtils.js";
import { getFriendList, getProfile } from "../profile/getProfile.js";
import { router } from "../main.js";
import { constructFriendsListId } from "./utilsChat.js";
import { injectFriendsInChat } from "./injectChat.js";
import { etablishConnectionWebSocket } from "./websocketChat.js";
import { injectUsersNotFriendsInChat } from "./injectChat.js";
import { handleSendButton } from "./attashListenerChat.js";
import { createConversationObjects } from "./utilsChat.js";
import { attachSearchListenerChat } from "./attashListenerChat.js";

export let conversations = {};
export let currentFriendId;
export let chatSocket;
export let senderId;
export let clientSender;
export let blocked_users = [];

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
    await attachSearchListenerChat(friendsListIds);
    createConversationObjects(friends, clientSender);
  } catch (error) {
    console.error("Error:", error);
    router("/home");
  }
}

export function resetCurrentFriendId() {
  currentFriendId = null;
}

export function setWebSocket(ws) {
  chatSocket = ws;
}

export function setCurrentFriendId(uid) {
  currentFriendId = uid;
}
