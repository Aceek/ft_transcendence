

export async function handleTournamentMessage(data) {
 const {type, message, tournamentId, action} = data;
  if (action === "tournament_ready") {
    console.log("Tournament ready");
    // Show a notification that the tournament is ready
    // Redirect to the tournament page
  } else if (action === "tournament_end") {
    console.log("Tournament end");
    // Show a notification that the tournament ended
    // Redirect to the tournament page
  }
}