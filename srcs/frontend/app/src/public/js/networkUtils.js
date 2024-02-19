import { api_url, credentialsOption } from "./main.js";

export async function isAPIConnected() {
  try {
    let response = await fetch(api_url + "auth/ping/", {
      method: "GET",
      credentials: credentialsOption,
    });
    if (response.status === 200) {
      return true;
    } else {
      response = await fetch(api_url + "auth/refresh/", {
        method: "POST",
        credentials: credentialsOption,
      });
      return response.status === 200;
    }
  } catch (error) {
    console.error("Error:", error);
    return false;
  }
}