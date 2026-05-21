from itertools import combinations

from django.core.management.base import BaseCommand
from django.db import transaction

from tournament.models import Group, Team, Match

BRACKET_GROUPS = {
    "A": [
        ("Arthur", "Flavio"),
        ("Rogerio", "Ana"),
        ("Jonas", "Valmir"),
        ("Tati", "Danilo"),
        ("Crepaldi", "Angela"),
    ],
    "B": [
        ("Joao Vitor (Tati)", "Flavia"),
        ("Fabio", "Virginia"),
        ("Pena", "Vincent"),
        ("Luciano", "Marie"),
        ("Bustos", "Joao"),
    ],
    "C": [
        ("Aoki", "Bruno"),
        ("Pava", "Fernanda"),
        ("Andre Hideki", "Joao Vitor (CPD)"),
        ("Sergio", "Adriano"),
    ],
}

PLAYOFF_MATCHES = [
    {
        "match_number": 1,
        "phase": Match.PHASE_PLACEMENT_9_14,
        "bracket_type": Match.BRACKET_PLACEMENT,
        "best_of": 1,
        "source_team_a": "5o Grupo A",
        "source_team_b": "5o Grupo B",
        "final_position_loser": 14,
        "sort_order": 1,
    },
    {
        "match_number": 2,
        "phase": Match.PHASE_PLACEMENT_9_14,
        "bracket_type": Match.BRACKET_PLACEMENT,
        "best_of": 1,
        "source_team_a": "Vencedor jogo 1",
        "source_team_b": "4o Grupo C",
        "source_match_a_number": 1,
        "source_match_a_is_winner": True,
        "final_position_loser": 13,
        "final_position_winner": 12,
        "sort_order": 2,
    },
    {
        "match_number": 3,
        "phase": Match.PHASE_PLACEMENT_9_14,
        "bracket_type": Match.BRACKET_PLACEMENT,
        "best_of": 1,
        "source_team_a": "4o Grupo A",
        "source_team_b": "4o Grupo B",
        "final_position_loser": 11,
        "sort_order": 3,
    },
    {
        "match_number": 4,
        "phase": Match.PHASE_PLACEMENT_9_14,
        "bracket_type": Match.BRACKET_PLACEMENT,
        "best_of": 1,
        "source_team_a": "Vencedor jogo 3",
        "source_team_b": "3o Grupo C",
        "source_match_a_number": 3,
        "source_match_a_is_winner": True,
        "final_position_loser": 10,
        "final_position_winner": 9,
        "sort_order": 4,
    },
    {
        "match_number": 5,
        "phase": Match.PHASE_QUARTERFINAL,
        "bracket_type": Match.BRACKET_MAIN,
        "best_of": 3,
        "source_team_a": "1o Grupo A",
        "source_team_b": "3o Grupo B",
        "sort_order": 5,
    },
    {
        "match_number": 6,
        "phase": Match.PHASE_QUARTERFINAL,
        "bracket_type": Match.BRACKET_MAIN,
        "best_of": 3,
        "source_team_a": "1o Grupo C",
        "source_team_b": "2o Grupo A",
        "sort_order": 6,
    },
    {
        "match_number": 7,
        "phase": Match.PHASE_QUARTERFINAL,
        "bracket_type": Match.BRACKET_MAIN,
        "best_of": 3,
        "source_team_a": "1o Grupo B",
        "source_team_b": "3o Grupo A",
        "sort_order": 7,
    },
    {
        "match_number": 8,
        "phase": Match.PHASE_QUARTERFINAL,
        "bracket_type": Match.BRACKET_MAIN,
        "best_of": 3,
        "source_team_a": "2o Grupo B",
        "source_team_b": "2o Grupo C",
        "sort_order": 8,
    },
    {
        "match_number": 9,
        "phase": Match.PHASE_FIFTH_TO_EIGHTH,
        "bracket_type": Match.BRACKET_MAIN,
        "best_of": 3,
        "source_team_a": "Perdedor jogo 5",
        "source_team_b": "Perdedor jogo 6",
        "source_match_a_number": 5,
        "source_match_a_is_winner": False,
        "source_match_b_number": 6,
        "source_match_b_is_winner": False,
        "sort_order": 9,
    },
    {
        "match_number": 10,
        "phase": Match.PHASE_FIFTH_TO_EIGHTH,
        "bracket_type": Match.BRACKET_MAIN,
        "best_of": 3,
        "source_team_a": "Perdedor jogo 7",
        "source_team_b": "Perdedor jogo 8",
        "source_match_a_number": 7,
        "source_match_a_is_winner": False,
        "source_match_b_number": 8,
        "source_match_b_is_winner": False,
        "sort_order": 10,
    },
    {
        "match_number": 11,
        "phase": Match.PHASE_FIFTH_TO_EIGHTH,
        "bracket_type": Match.BRACKET_MAIN,
        "best_of": 3,
        "source_team_a": "Perdedor jogo 9",
        "source_team_b": "Perdedor jogo 10",
        "source_match_a_number": 9,
        "source_match_a_is_winner": False,
        "source_match_b_number": 10,
        "source_match_b_is_winner": False,
        "final_position_winner": 7,
        "final_position_loser": 8,
        "sort_order": 11,
    },
    {
        "match_number": 12,
        "phase": Match.PHASE_FIFTH_TO_EIGHTH,
        "bracket_type": Match.BRACKET_MAIN,
        "best_of": 3,
        "source_team_a": "Vencedor jogo 9",
        "source_team_b": "Vencedor jogo 10",
        "source_match_a_number": 9,
        "source_match_a_is_winner": True,
        "source_match_b_number": 10,
        "source_match_b_is_winner": True,
        "final_position_winner": 5,
        "final_position_loser": 6,
        "sort_order": 12,
    },
    {
        "match_number": 13,
        "phase": Match.PHASE_SEMIFINAL,
        "bracket_type": Match.BRACKET_MAIN,
        "best_of": 3,
        "source_team_a": "Vencedor jogo 5",
        "source_team_b": "Vencedor jogo 6",
        "source_match_a_number": 5,
        "source_match_a_is_winner": True,
        "source_match_b_number": 6,
        "source_match_b_is_winner": True,
        "sort_order": 13,
    },
    {
        "match_number": 14,
        "phase": Match.PHASE_SEMIFINAL,
        "bracket_type": Match.BRACKET_MAIN,
        "best_of": 3,
        "source_team_a": "Vencedor jogo 7",
        "source_team_b": "Vencedor jogo 8",
        "source_match_a_number": 7,
        "source_match_a_is_winner": True,
        "source_match_b_number": 8,
        "source_match_b_is_winner": True,
        "sort_order": 14,
    },
    {
        "match_number": 15,
        "phase": Match.PHASE_THIRD_PLACE,
        "bracket_type": Match.BRACKET_MAIN,
        "best_of": 3,
        "source_team_a": "Perdedor jogo 13",
        "source_team_b": "Perdedor jogo 14",
        "source_match_a_number": 13,
        "source_match_a_is_winner": False,
        "source_match_b_number": 14,
        "source_match_b_is_winner": False,
        "final_position_winner": 3,
        "final_position_loser": 4,
        "sort_order": 15,
    },
    {
        "match_number": 16,
        "phase": Match.PHASE_FINAL,
        "bracket_type": Match.BRACKET_MAIN,
        "best_of": 3,
        "source_team_a": "Vencedor jogo 13",
        "source_team_b": "Vencedor jogo 14",
        "source_match_a_number": 13,
        "source_match_a_is_winner": True,
        "source_match_b_number": 14,
        "source_match_b_is_winner": True,
        "final_position_winner": 1,
        "final_position_loser": 2,
        "sort_order": 16,
    },
]


class Command(BaseCommand):
    help = "Cria dados iniciais do campeonato: grupos, duplas e partidas"

    def handle(self, *args, **options):
        with transaction.atomic():
            self._seed(options)

    def _seed(self, options):
        groups_created, teams_created, matches_created = 0, 0, 0

        for group_name, team_list in BRACKET_GROUPS.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                groups_created += 1
                self.stdout.write(f"  Grupo {group.name} criado")

            for p1, p2 in team_list:
                _, created = Team.objects.get_or_create(
                    player1_name=p1,
                    player2_name=p2,
                    group=group,
                )
                if created:
                    teams_created += 1

        self.stdout.write(
            f"\n{groups_created} grupo(s), {teams_created} dupla(s) criada(s)"
        )

        for group in Group.objects.all():
            teams = list(group.teams.all())
            existing = Match.objects.filter(
                bracket_type=Match.BRACKET_GROUP,
                group=group,
            ).count()
            expected = len(list(combinations(teams, 2)))

            if existing >= expected:
                self.stdout.write(
                    f"  Partidas do Grupo {group.name} ja existem ({existing})"
                )
                continue

            match_number = (
                Match.objects.filter(
                    bracket_type=Match.BRACKET_GROUP,
                )
                .order_by("-match_number")
                .first()
            )
            counter = match_number.match_number + 1 if match_number else 1000

            sort_offset = 0
            for group_obj in Group.objects.order_by("name"):
                if group_obj == group:
                    break
                sort_offset += len(list(combinations(list(group_obj.teams.all()), 2)))

            sort_counter = sort_offset

            for i, (team_a, team_b) in enumerate(combinations(teams, 2)):
                _, created = Match.objects.get_or_create(
                    match_number=counter + i,
                    bracket_type=Match.BRACKET_GROUP,
                    defaults={
                        "phase": Match.PHASE_GROUP,
                        "group": group,
                        "team_a": team_a,
                        "team_b": team_b,
                        "status": Match.STATUS_READY,
                        "best_of": 3,
                        "sort_order": sort_counter + i,
                    },
                )
                if created:
                    matches_created += 1

        self.stdout.write(f"{matches_created} partida(s) de grupo criada(s)")

        playoff_created = 0
        for match_data in PLAYOFF_MATCHES:
            _, created = Match.objects.get_or_create(
                match_number=match_data["match_number"],
                bracket_type=match_data["bracket_type"],
                defaults={
                    "phase": match_data["phase"],
                    "best_of": match_data["best_of"],
                    "source_team_a": match_data.get("source_team_a", ""),
                    "source_team_b": match_data.get("source_team_b", ""),
                    "final_position_winner": match_data.get("final_position_winner"),
                    "final_position_loser": match_data.get("final_position_loser"),
                    "sort_order": match_data["sort_order"],
                    "status": Match.STATUS_BLOCKED,
                },
            )
            if created:
                playoff_created += 1

        self._link_source_matches()

        self.stdout.write(f"{playoff_created} partida(s) de playoff criada(s)")

        total_groups = Group.objects.count()
        total_teams = Team.objects.count()
        total_matches = Match.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTotal: {total_groups} grupo(s), "
                f"{total_teams} dupla(s), "
                f"{total_matches} partida(s)"
            )
        )

    def _link_source_matches(self):
        for match_data in PLAYOFF_MATCHES:
            match = Match.objects.filter(
                match_number=match_data["match_number"],
                bracket_type=match_data["bracket_type"],
            ).first()
            if not match:
                continue

            updated = False

            if "source_match_a_number" in match_data:
                source = Match.objects.filter(
                    match_number=match_data["source_match_a_number"],
                    bracket_type=match.bracket_type,
                ).first()
                if source:
                    match.source_match_a = source
                    match.source_match_a_is_winner = match_data.get(
                        "source_match_a_is_winner"
                    )
                    updated = True

            if "source_match_b_number" in match_data:
                source = Match.objects.filter(
                    match_number=match_data["source_match_b_number"],
                    bracket_type=match.bracket_type,
                ).first()
                if source:
                    match.source_match_b = source
                    match.source_match_b_is_winner = match_data.get(
                        "source_match_b_is_winner"
                    )
                    updated = True

            if updated:
                match.save()
