import { changeUrlHistory, addEventListenerById, loadProfileCss, loadScript } from "../pageUtils.js";
import { router } from "../main.js";


function addEventListeners() {
    addEventListenerById("play-button", "click", function (event) {
        event.preventDefault();
        // router("/play");
        getPongGamePage();
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

function getPongGamePage() {
  fetch('public/html/pong.html')
      .then(response => response.text())
      .then(template => {
          document.getElementById('main').innerHTML = template;
          loadProfileCss("/public/css/pong.css")
          const script = document.createElement("script");
          script.src = "public/js/pong/pong.js";
          document.head.appendChild(script);
      });
}