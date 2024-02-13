import { getDataWithToken } from "../pageUtils.js";
import { api_url } from "../main.js";

export async function getProfile(UID = null) {
  let urlProfile = api_url + "users/profile/me";
  if (UID) {
    urlProfile = api_url + `users/profile/${UID}`;
  }
  const response = await getDataWithToken(urlProfile);
  if (!response.ok) {
    throw new Error("Failed to get profile");
  }
  const data = await response.json();
  return data;
}

export async function getFriendList(page = 1) {
  let url = `${api_url}users/friends?page=${page}`;
  if (page === 0) {
    url = `${api_url}users/friends`;
  }
  console.log('url:', url)
  const response = await getDataWithToken(url);
  if (!response.ok) {
    throw new Error("Failed to get friend list");
  }
  const data = await response.json();
  if (data.results) {
    return {
      results: data.results,
      nextPage: data.next,
      prevPage: data.previous,
    };
  } else {
    return {
      results: data,
    };
  }
}

export async function getGameHistory(page = 1, UID = null) {
  let urlHistory = `${api_url}history/me?page=${page}`;
  if (UID) {
    urlHistory = `${api_url}history/${UID}?page=${page}`;
  }
  const response = await getDataWithToken(urlHistory);
  if (!response.ok) {
    throw new Error("Failed to get game history");
  }
  const history = await response.json();
  return {
    results: history.results,
    nextPage: history.next,
    prevPage: history.previous,
  };
}
