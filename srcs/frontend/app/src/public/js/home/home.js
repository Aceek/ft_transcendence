import { changeUrlHistory, addEventListenerById, loadProfileCss, loadScript } from "../pageUtils.js";
import { router } from "../main.js";


function addEventListeners() {
    addEventListenerById("play-button", "click", function (event) {
        event.preventDefault();
        router("/play");
    });
}

export function getHomePage() {
  fetch("/public/html/home.html")
    .then((response) => response.text())
    .then((template) => {
      document.getElementById("main").innerHTML = template;
      loadProfileCss("/public/css/home.css")
      addEventListeners();
      changeUrlHistory("/home");
    });

}
