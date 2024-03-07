import { api_url, router } from "../main.js";
import { fetchTemplate, loadProfileCss } from "../pageUtils.js";
import {
  sendUpdateRequest,
  injectFriendList,
  injectUserInfo,
  prepareUpdateData,
  printConfirmationMessage,
  injectHistoryList,
} from "./profileUtils.js";
import { getProfile } from "./getProfile.js";
import { injectFriendsSearsh } from "./searchFriends.js";
import { extractErrorMessages } from "../tournament/getUtils.js";

export async function displayProfile() {
  loadProfileCss("/public/css/profile.css");
  try {
    const profileHtml = await fetchTemplate("/public/html/profile.html");
    document.getElementById("main").innerHTML = profileHtml;
    const profile = await getProfile();
    injectUserInfo(profile);
    await injectFriendList();
    await injectHistoryList();
    injectFriendsSearsh();
    await attachSubmitListener(profile);
    await changeAvatar(profile);

  } catch (error) {
    console.error("Error:", error);
    router("/home");
  }
}

async function attachSubmitListener(profile) {
  document
    .getElementById("username")
    .addEventListener("keydown", async function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        await handleSubmit(profile);
      }
    });

  document
    .getElementById("email")
    .addEventListener("keydown", async function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        await handleSubmit(profile);
      }
    });

  const statsButton = document.getElementById("statsButton");
  statsButton.addEventListener("click", async () => {
    await router("/profile/stats");
  });
  statsButton.disabled = false;

  const profileButton = document.getElementById("profileButton");
  profileButton.disabled = true;
}

function updateProfileAndPrintMessages(profile, dataToUpdate, fields) {
  fields.forEach((field) => {
    const isNewEmail = field === "email" && dataToUpdate["new_email"];
    if (dataToUpdate[field] || isNewEmail) {
      const value = document.getElementById(field).value;
      if (field !== "email") profile[field] = value;
      let message = "";
      if (field === "email") {
        message = "Verifié votre nouveau mail pour confirmer le changement.";
      } else if (field === "username") {
        message = "Nom d'utilisateur modifié avec succès.";
      }
      if (message) printConfirmationMessage(message);
    }
  });
}

async function handleSubmit(profile) {
  const fields = ["username", "email"];
  const dataToUpdate = prepareUpdateData(profile, fields);

  if (Object.keys(dataToUpdate).length === 0) return;

  const updateSuccess = await sendUpdateRequest(
    api_url + "users/profile/update",
    dataToUpdate
  );

  if (updateSuccess.success) {
    updateProfileAndPrintMessages(profile, dataToUpdate, fields);
    document.getElementById("email").value = profile.email;
  } else {
    let errorMessage = await updateSuccess.response.json();
    errorMessage = extractErrorMessages(errorMessage);
    printConfirmationMessage(errorMessage, "emailDiv", "red");
    document.getElementById("username").value = profile.username;
    document.getElementById("email").value = profile.email;
  }
}

function updateAvatarImage(file) {
  const reader = new FileReader();
  reader.onload = function (e) {
    document.getElementById("avatar").src = e.target.result;
    if (navbarAvatar) navbarAvatar.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

export async function changeAvatar(profile) {
  document
    .getElementById("avatarUpload")
    .addEventListener("change", async function () {
      const file = this.files[0];

      if (!file) return;

      const formData = new FormData();
      formData.append("avatar", file);

      const updateSuccess = await sendUpdateRequest(
        api_url + "users/profile/update",
        formData
      );

      if (updateSuccess.success) {
        console.log("Avatar modification réussie !");
        updateAvatarImage(file);
      } else {
        console.error("Erreur lors de la modification de l'avatar.");
      }
    });
}
