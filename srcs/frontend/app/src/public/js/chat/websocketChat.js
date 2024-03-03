import { processChatMessage } from "./utilsChat.js";
import { getProfile } from "../profile/getProfile.js";
import { injectChatRoom } from "./injectChat.js";
import { incressBadgeBgSuccess } from "./utilsChat.js";
import { handleTournamentMessage } from "./tournamentChat.js";
import {
  conversations,
  chatSocket,
  currentFriendId,
  clientSender,
  setWebSocket,
} from "./chat.js";

export function handleWebSocketOpen(friendsListIds, resolve) {
  console.log("Connection opened");
  resolve();
}

export function handleWebSocketMessage(event, friendsListIds) {
  const data = JSON.parse(event.data);
  switch (data.type) {
    case "chat_message":
      processChatMessage(data, friendsListIds);
      break;
    case "ping":
      chatSocket.send(JSON.stringify({ type: "pong", action: "pong" }));
      break;
    case "tournament_message":
      handleTournamentMessage(data);
      break;
    case "match_message":
      handleTournamentMessage(data);
      break;
    default:
      console.log("Unknown message type:", data);
  }
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
      resolve();
      return;
    }
    const newChatSocket = new WebSocket("wss://localhost/ws/chat");
    setWebSocket(newChatSocket);

    chatSocket.onopen = () => handleWebSocketOpen(friendsListIds, resolve);
    chatSocket.onmessage = (event) =>
      handleWebSocketMessage(event, friendsListIds);
    chatSocket.onclose = () => handleWebSocketClose(reject);
    chatSocket.onerror = (error) => handleWebSocketError(error, reject);
  });
}

export function sendReadStatus(uid) {
  if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
    chatSocket.send(
      JSON.stringify({
        action: "read_messages",
        receiver: uid,
      })
    );
  }
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

export function handleOutgoingMessage(data) {
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



