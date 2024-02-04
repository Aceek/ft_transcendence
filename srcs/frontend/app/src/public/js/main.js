// import { getLoginPage, checkOAuthCode } from "./login.js";
// import { getHomePage } from "./home.js";
// import { getRegisterPage } from "./register.js";
// import { isAPIConnected } from "./ping.js";

// export const api_url = "http://localhost:8000/api/";

// export async function router() {
//   const path = window.location.pathname;

//   if (await isAPIConnected()) {
//     switch (path) {
//       case "/home":
//         getHomePage();
//         break;
//       case "/register":
//         getRegisterPage();
//         break;
//       default:
//         getHomePage();
//         break;
//     }
//   } else if (await checkOAuthCode()) {
//     router("/home");
//     return;
//   } else {
//     getLoginPage();
//   }
// }

// router();


import { getLoginPage, checkOAuthCode } from "./login.js";
import { getHomePage } from "./home.js";
import { getRegisterPage } from "./register.js";
import { isAPIConnected } from "./ping.js";

export const api_url = "http://localhost:8000/api/";

export async function router() {
  const path = window.location.pathname; // Obtenez le chemin de l'URL sans le "#"

  console.log(`Navigating to path: ${path}`); // Log du chemin de l'URL

  if (await isAPIConnected()) {
    switch (path) {
      case "/home":
        console.log("Loading home page");
        getHomePage();
        break;
      case "/register":
        console.log("Loading register page");
        getRegisterPage();
        break;
      // Ajoutez d'autres routes ici
      default:
        console.log("Loading default page");
        getHomePage(); // Page par défaut si aucune route ne correspond
        break;
    }
  } else if (await checkOAuthCode()) {
    console.log("User has OAuth code, redirecting to home page");
    router("/home"); // Redirection vers la page d'accueil si l'API est connectée
    return;
  } else {
    console.log("User is not authenticated, loading login page");
    getLoginPage(); // Page de connexion par défaut
  }
}

router();
