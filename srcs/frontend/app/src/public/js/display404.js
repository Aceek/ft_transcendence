import { fetchTemplate, loadProfileCss } from "./pageUtils.js";

export async function display404() {
  loadProfileCss("/public/css/404.css");
  const templateHtml = await fetchTemplate("/public/html/404.html");
  document.getElementById("main").innerHTML = templateHtml;
}
