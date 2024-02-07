import { getDataWithToken } from "../pageUtils.js";
import { api_url } from "../main.js";

export async function getProfile() {
  const urlProfile = api_url + "users/profile/me";
  const response = await getDataWithToken(urlProfile);
  if (!response.ok) {
    throw new Error("Failed to get profile");
  }
  const data = await response.json();
  return data;
}

export async function getFriendList() {
  const url = api_url + "users/friends";
  const response = await getDataWithToken(url);
  if (!response.ok) {
    throw new Error("Failed to get friend list");
  }
  const data = await response.json();
  return data;
}

export async function getGameHistory(page = 1) {
  const urlHistory = `${api_url}history/me?page=${page}`;
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
