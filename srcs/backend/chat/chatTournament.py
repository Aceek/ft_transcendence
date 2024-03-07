import json
from channels.db import database_sync_to_async

class ChatTournamentMixin:
    async def tournament_message(self, event):
        message = event["message"]
        action = event.get("action")
        tournament_id = event["tournamentId"]
        await self.send(
            text_data=json.dumps(
                {
                    "type": "tournament_message",
                    "message": message,
                    "tournamentId": tournament_id,
                    "action": action,
                }
            )
        )

    async def send_tournament(self, event):
        tournament_id = event["tournamentId"]
        action = event["action"]
        if (action == "join_tournament"):
            await self.channel_layer.group_add(
                f"tournament_{tournament_id}", self.channel_name
            )
            return
        await self.send(
            text_data=json.dumps(
                {
                    "type": "tournament_message",
                    "action": action,
                    "tournamentId": tournament_id,
                    "message": "Tournament " + tournament_id + " is ready",
                }
            )
        )

    async def send_tournament_ready(self, active_tournaments):
        for tournament in active_tournaments:
            await self.channel_layer.group_add(
                f"tournament_{str(tournament.uid)}", self.channel_name
            )
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "tournament_message",
                        "action": "tournament_ready",
                        "tournamentId": str(tournament.uid),
                        "message": "Tournament " + str(tournament.uid) + " is ready",
                    }
                )
            )

    async def send_match(self, event):
        match_id = event["matchId"]
        message = event["message"]
        action = event["action"]
        tournamentId = event.get("tournamentId")

        if (action == "join_match"):
            print(f"Received match event: {event}")
            await self.channel_layer.group_add(f"match_{match_id}", self.channel_name)
            return
        await self.send(
            text_data=json.dumps(
                {
                    "type": "match_message",
                    "action": action,
                    "matchId": match_id,
                    "message": message,
                    "tournamentId": tournamentId,
                }
            )
        )

    async def verify_active_match(self):
        active_matches = await self.get_active_matches()
        await self.send_match_ready(active_matches)

    @database_sync_to_async
    def get_active_matches(self):
        from tournament.models import Matches
        from django.db.models import Q

        active_matches = Matches.objects.filter(
            Q(user1=self.user) | Q(user2=self.user),
            is_active=True,
            is_finished=False,
        )
        return list(active_matches)

    @database_sync_to_async
    def get_tourmanent_uid(self, match):
        return str(match.tournament.uid)

    async def send_match_ready(self, active_matches):
        for match in active_matches:
            tournamentUID = await self.get_tourmanent_uid(match)
            await self.channel_layer.group_add(
                f"match_{str(match.uid)}", self.channel_name
            )
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "match_message",
                        "action": "match_ready",
                        "matchId": str(match.uid),
                        "message": "Match " + str(match.uid) + " is ready for tournament " + tournamentUID,
                        "tournamentId": tournamentUID,
                    }
                )
            )

    async def verify_active_tournament(self):
        active_tournaments = await self.get_active_tournaments()
        await self.send_tournament_ready(active_tournaments)

    @database_sync_to_async
    def get_active_tournaments(self):
        from tournament.models import Tournament

        active_tournaments = Tournament.objects.filter(
            is_active=True, user=self.user, is_finished=False
        )
        return list(active_tournaments)
