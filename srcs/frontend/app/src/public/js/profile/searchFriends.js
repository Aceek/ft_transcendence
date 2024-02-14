import { requestDataWithToken } from "../pageUtils.js";
import { api_url } from "../main.js";
import {
  injectFriendList,
  onclickFunctionDeleteContainer,
  friendContext,
} from "./profileUtils.js";
import { createButtonFriend } from "./profileFriends.js";

export function injectFriendsSearsh() {
  const friendListCol = document.getElementById("friends-list-col");
  const createFriendsSearch = document.createElement("div");
  createFriendsSearch.id = "friendsSearch";
  createFriendsSearch.className = "input-group mb-3";
  createFriendsSearch.innerHTML = `
    <input type="text" id="searchFriends" class="form-control" 
    placeholder="Search users" aria-label="Search friends"
    aria-describedby="button-addon2">
  `;
  friendListCol.insertBefore(createFriendsSearch, friendListCol.firstChild);

  attachSearchListener();
}

async function displayUsersInSearch(usersInSearch) {
  const friendsList = document.getElementById("friendsList");
  friendsList.innerHTML = "";
  if (usersInSearch.length > 5) {
    usersInSearch = usersInSearch.slice(0, 5);
  }
  await usersInSearch.forEach(async (user) => {
    const listItem = document.createElement("li");
    listItem.className =
      "list-group-item d-flex align-items-center justify-content-between";

    listItem.innerHTML = `
      <div class="friend-info d-flex align-items-center">
        <img src="${user.avatar || "/public/images/profile.jpg"}" alt="Avatar de ${user.username}" class="rounded-circle me-3" width="75" height="75">
        <div>
          <a href="/profile/${user.id}"><strong>${user.username}</strong></a>
          <span class="text-success ms-2">• En ligne</span>
        </div>
      </div>
    `;
    addRemoveorAddButton(listItem, user.id);
    friendsList.appendChild(listItem);
  });
}

async function addRemoveorAddButton(listItem, userUID) {
  try {
    let profile = await requestDataWithToken(
      api_url + "users/friends",
      null,
      "GET"
    );
    profile = await profile.json();
    const isFriend = profile.some((friend) => friend.id === userUID);

    if (isFriend) {
      const removeButton = await createButtonFriend(
        userUID,
        "users/remove_friends",
        () => {
          onclickFunctionDeleteContainer(listItem);
        }
      );
      removeButton.textContent = "Remove";
      removeButton.classList.add("btn-danger");
      listItem.appendChild(removeButton);
    } else {
      const addButton = await createButtonFriend(
        userUID,
        "users/profile/update",
        () => {
          onclickFunctionDeleteContainer(listItem);
        }
      );
      listItem.appendChild(addButton);
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

function attachSearchListener() {
  const searchFriends = document.getElementById("searchFriends");
  searchFriends.addEventListener("input", async () => {
    const searchValue = searchFriends.value;
    if (searchValue.length > 0) {
      let usersInSearch = {};
      try {
        usersInSearch = await requestDataWithToken(
          api_url + "users?search=" + searchValue,
          null,
          "GET"
        );
        usersInSearch = await usersInSearch.json();
        const friendlistTitle = document.getElementById("friendListTitle");
        friendlistTitle.textContent = "User in search"
        displayUsersInSearch(usersInSearch);
      } catch (error) {
        console.error("Error:", error);
      }
    } else {
      friendContext.currentPage = 1;
      await injectFriendList();
    }
  });
}
