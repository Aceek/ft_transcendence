import { api_url } from "../main.js";

async function getProfile() {
  const urlProfile = api_url + "users/profile/me";
  const response = await fetch(urlProfile);
  if (!response.ok) {
    throw new Error("Failed to get profile");
  }
  const data = await response.json();
  return data;
}

export async function displayProfile() {
  try {
    const profile = await getProfile();

    const response = await fetch("public/html/profile.html");
    const profileBlock = response.text();

    document.getElementById("main").innerHTML = profileBlock;

    document.getElementById("avatar").src = profile.avatar;
    document.getElementById("username").textContent = profile.username;
    document.getElementById("email").textContent = profile.email;
    document.getElementById("2fa").textContent = profile.is_2fa_enabled
      ? "2FA is enabled"
      : "2FA is not enabled";
    document.getElementById("friends").innerHTML = profile.friends
      .map((friend) => `<li>${friend}</li>`)
      .join("");
  } catch (error) {
    console.error("Error:", error);
  }
}
