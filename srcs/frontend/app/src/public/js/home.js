import { changeUrlHistory, addEventListenerById } from "./pageUtils.js";
import { router } from "./main.js";


function addEventListeners() {
    addEventListenerById("profile-btn", "click", function (event) {
        event.preventDefault();
        router("/profile");
    });
}

export function getHomePage() {
  fetch("public/html/home.html")
    .then((response) => response.text())
    .then((template) => {
      document.getElementById("main").innerHTML = template;
      addEventListeners();
      changeUrlHistory("/home");
    });
}
