import { getDataWithToken } from "../pageUtils.js";
import { api_url, router } from "../main.js";

export async function getTournamentList(page = 1) {
  let url = `${api_url}play/tournaments?page=${page}`;
  if (page === 0) {
    url = `${api_url}play/tournaments/me`;
  }
  const response = await getDataWithToken(url);
  if (!response.ok) {
    throw new Error("Failed to get tournament list");
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

export async function getTournamentOwnedList() {
  const url = `${api_url}play/tournaments/me/owned`;
  const response = await getDataWithToken(url);
  if (!response.ok) {
    throw new Error("Failed to get tournament list");
  }
  const data = await response.json();
  return data;
}

export async function getTournamentByUID(tournamentUID) {
  const url = `${api_url}play/tournaments/${tournamentUID}/retrieve`;
  const response = await getDataWithToken(url);
  if (!response.ok) {
    throw new Error("Failed to get tournament");
  }
  const data = await response.json();
  return data;
}

export async function getTournamentHistory() {
  const url = `${api_url}play/tournaments/history`;
  const response = await getDataWithToken(url);
  if (!response.ok) {
    throw new Error("Failed to get tournament history");
  }
  const data = await response.json();
  return data;
}