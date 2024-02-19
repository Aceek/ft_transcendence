import { getDataWithToken } from "../pageUtils.js";
import { api_url, router } from "../main.js";


export async function getTournamentList(page = 1) {
  let url = `${api_url}play/tournaments?page=${page}`;
  if (page === 0) {
    url = `${api_url}play/tournaments/me`;
  }
  try {
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
  } catch (error) {
    console.error("Error:", error);
    router("/home");
  }
}