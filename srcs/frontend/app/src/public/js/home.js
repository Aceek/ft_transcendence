export function getHomePage() {
  fetch("public/html/home.html")
    .then((response) => response.text())
    .then((template) => {
      document.getElementById("main").innerHTML = template;
    });
}
