import { loadProfileCss, fetchTemplate } from "../pageUtils.js";
import { router } from "../main.js";
import { verifyifLocalTournament } from "./verificationLocal.js";
import {
  injectCreateLocalTournament,
  injectJoinAndDeleteLocalTournament,
  manageCreationLocalTournament,
} from "./utilsLocal.js";

export async function displayLocalPage() {
  try {
    loadProfileCss("/public/css/local.css");
    const localHtml = await fetchTemplate("/public/html/local.html");
    document.getElementById("main").innerHTML = localHtml;
    if (!(await verifyifLocalTournament())) {
      await injectCreateLocalTournament();
      await manageCreationLocalTournament();
    } else {
      injectJoinAndDeleteLocalTournament();
    }
  } catch (error) {
    console.error("Error:", error);
    router("/home");
  }
}
