import {
  fetchTemplate,
  loadProfileCss,
  requestDataWithToken,
} from "../../pageUtils.js";
import { api_url, router } from "../../main.js";
import { displayProfile } from "../profile.js";
import { displayFriendsProfile } from "../profileFriends.js";

async function verifyDOMProfileLoaded(userUID = null) {
  if (!document.getElementById("mainContainerProfile")) {
    if (userUID) {
      await displayFriendsProfile(userUID);
    } else {
      await displayProfile();
    }
  }
}

export async function displayStats(userUID = null) {
  await verifyDOMProfileLoaded(userUID);
  await fetchTemplate("/public/html/stats.html")
    .then(async (statsDivString) => {
      const friendHistoryDiv = document.getElementById("friendHistoryDiv");
      friendHistoryDiv.innerHTML = statsDivString;

      await loadScript("https://cdn.jsdelivr.net/npm/chart.js");
      try {
        const statsData = await fetchData(userUID);
        await displayListenProfileButton(userUID);
        displaySummary(statsData[0]);
        displayEloChart(statsData);
        displayWinLoseChart(statsData);
        displayWinLossRatioChart(statsData);
        addEventListenerForSelectorValue();
      } catch (error) {
        console.error(
          "Une erreur s'est produite lors de l'affichage de la chart :",
          error.message
        );
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

async function displayListenProfileButton(userUID = null) {
  const profileButton = document.getElementById("profileButton");
  profileButton.addEventListener("click", async () => {
    if (userUID) {
      router(`/profile/${userUID}`);
    } else {
      router("/profile");
    }
  });
  profileButton.disabled = false;

  const statsButton = document.getElementById("statsButton");
  statsButton.disabled = true;
}

async function displaySummary(data) {
  try {
    loadProfileCss("/public/css/stats.css");
    loadProfileCss(
      "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css"
    );
    const summaryContainer = document.getElementById("summary");
    summaryContainer.innerHTML = `
      <div class="summary-title">Résumé des statistiques :</div>
      <div class="summary-stat"><i class="fas fa-trophy icon"></i>Victoires : ${data.win}</div>
      <div class="summary-stat"><i class="fas fa-thumbs-down icon"></i>Défaites : ${data.lose}</div>
      <div class="summary-stat"><i class="fas fa-chart-line icon"></i>ELO : ${data.elo}</div>
      <div class="summary-stat"><i class="fas fa-fire icon"></i>Série de victoires : ${data.win_streak}</div>
      <div class="summary-stat"><i class="fas fa-snowflake icon"></i>Série de défaites : ${data.lose_streak}</div>
      <div class="summary-stat"><i class="fas fa-crown icon"></i>Plus grande série de victoires : ${data.biggest_win_streak}</div>
    `;
  } catch (error) {
    console.error(error.message);
  }
}

function addEventListenerForSelectorValue() {
  document
    .getElementById("chartSelector")
    .addEventListener("change", function () {
      var selectedChart = this.value;
      var allCharts = document.querySelectorAll("#chartContainer canvas");
      allCharts.forEach(function (chart) {
        if (chart.id === selectedChart + "Chart") {
          chart.style.display = "block";
        } else {
          chart.style.display = "none";
        }
      });
    });
}

async function fetchData(userUID) {
  try {
    let url = api_url + "stats/me";
    if (userUID) {
      url = api_url + "stats/" + `${userUID}`;
    }
    const response = await requestDataWithToken(url);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(error.message);
    throw error;
  }
}

async function displayWinLossRatioChart(data) {
  try {
    const ratio = data[0].win / (data[0].win + data[0].lose);

    const ctxWinLossRatio = document
      .getElementById("winLossRatioChart")
      .getContext("2d");
    const winLossRatioChart = new Chart(ctxWinLossRatio, {
      type: "doughnut",
      data: {
        labels: ["Victoires", "Défaites"],
        datasets: [
          {
            label: "Ratio de Victoires/Défaites",
            data: [ratio, 1 - ratio],
            backgroundColor: [
              "rgba(54, 162, 235, 0.6)",
              "rgba(255, 99, 132, 0.6)",
            ],
            borderColor: ["rgba(54, 162, 235, 1)", "rgba(255, 99, 132, 1)"],
            borderWidth: 1,
          },
        ],
      },
      options: {
        cutoutPercentage: 50,
        responsive: true,
        maintainAspectRatio: false,
      },
    });
  } catch (error) {
    console.error(error.message);
  }
}

async function displayWinLoseChart(data) {
  try {
    const victories = data[0].win;
    const defeats = data[0].lose;

    const ctxWinLose = document.getElementById("winLoseChart").getContext("2d");
    const winLoseChart = new Chart(ctxWinLose, {
      type: "bar",
      data: {
        labels: ["Victoires", "Défaites"],
        datasets: [
          {
            label: "Nombre de Victoires/Défaites",
            data: [victories, defeats],
            backgroundColor: [
              "rgba(54, 162, 235, 0.6)",
              "rgba(255, 99, 132, 0.6)",
            ],
            borderColor: ["rgba(54, 162, 235, 1)", "rgba(255, 99, 132, 1)"],
            borderWidth: 1,
          },
        ],
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
          },
        },
        responsive: true,
        maintainAspectRatio: false,
      },
    });
  } catch (error) {
    console.error(error.message);
  }
}

function displayEloChart(data) {
  const eloData = data[0].elo_history.map((entry) => entry.elo);
  const timestamps = data[0].elo_history.map(
    (entry) => new Date(entry.created_at)
  );
  const labels = timestamps.map((timestamp) => timestamp.toLocaleTimeString());
  eloData.reverse();
  labels.reverse();
  const ctxElo = document.getElementById("eloChart").getContext("2d");
  const eloChart = new Chart(ctxElo, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "10 last games elo history",
          data: eloData,
          backgroundColor: "rgba(75, 192, 192, 0.2)",
          borderColor: "rgba(75, 192, 192, 1)",
          fill: false,
        },
      ],
    },
    options: {
      scales: {
        y: {
          beginAtZero: false,
        },
      },
      responsive: true,
      maintainAspectRatio: false,
    },
  });
}

function loadScript(url) {
  return new Promise((resolve, reject) => {
    const existingScript = document.querySelector(`script[src="${url}"]`);
    if (existingScript) {
      resolve();
      return;
    }

    const script = document.createElement("script");
    script.src = url;
    script.onload = resolve;
    script.onerror = reject;
    document.body.appendChild(script);
  });
}
