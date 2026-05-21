from django.core.management.base import BaseCommand
from django.db import transaction

from tournament.models import Double, Group, Match
from tournament.services import ensure_sets, ensure_bracket_exists

BRACKET_DOUBLES = {
    "A": [
        ("Arthur / Flavio", "Arthur", "Flavio"),
        ("Rogerio / Ana", "Rogerio", "Ana"),
        ("Jonas / Valmir", "Jonas", "Valmir"),
        ("Tati / Danilo", "Tati", "Danilo"),
        ("Crepaldi / Angela", "Crepaldi", "Angela"),
    ],
    "B": [
        ("Joao Vitor (Tati) / Flavia", "Joao Vitor (Tati)", "Flavia"),
        ("Fabio / Virginia", "Fabio", "Virginia"),
        ("Pena / Vincent", "Pena", "Vincent"),
        ("Luciano / Marie", "Luciano", "Marie"),
        ("Bustos / Joao", "Bustos", "Joao"),
    ],
    "C": [
        ("Aoki / Bruno", "Aoki", "Bruno"),
        ("Pava / Fernanda", "Pava", "Fernanda"),
        ("Andre Hideki / Joao Vitor (CPD)", "Andre Hideki", "Joao Vitor (CPD)"),
        ("Sergio / Adriano", "Sergio", "Adriano"),
    ],
}

GROUP_MATCHES = {
    "A": [(0, 1), (2, 3), (4, 0), (1, 2), (3, 4), (0, 2), (1, 3), (4, 2), (0, 3), (1, 4)],
    "B": [(0, 1), (2, 3), (4, 0), (1, 2), (3, 4), (0, 2), (1, 3), (4, 2), (0, 3), (1, 4)],
    "C": [(0, 1), (2, 3), (0, 2), (1, 3), (0, 3), (1, 2)],
}


class Command(BaseCommand):
    help = "Cria dados iniciais do campeonato: grupos, duplas e partidas"

    def handle(self, *args, **options):
        with transaction.atomic():
            self._seed()

    def _seed(self):
        groups_created, doubles_created, matches_created = 0, 0, 0

        doubles_by_group = {}

        for group_name, double_list in BRACKET_DOUBLES.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                groups_created += 1
                self.stdout.write(f"  Grupo {group.name} criado")

            group_doubles = []
            for name, p1, p2 in double_list:
                double, created = Double.objects.get_or_create(
                    name=name,
                    defaults={"player_1": p1, "player_2": p2},
                )
                if created:
                    doubles_created += 1
                group_doubles.append(double)
                group.doubles.add(double)

            doubles_by_group[group_name] = group_doubles

        self.stdout.write(
            f"\n{groups_created} grupo(s), {doubles_created} dupla(s) criada(s)"
        )

        for group_name, match_pairs in GROUP_MATCHES.items():
            group = Group.objects.get(name=group_name)
            existing = Match.objects.filter(
                phase=Match.PHASE_GROUP,
                group=group,
            ).count()
            expected = len(match_pairs)

            if existing >= expected:
                self.stdout.write(
                    f"  Partidas do Grupo {group.name} ja existem ({existing})"
                )
                continue

            sort_offset = 0
            for gn in ["A", "B", "C"]:
                if gn == group_name:
                    break
                sort_offset += len(GROUP_MATCHES.get(gn, []))

            counter_base = 1000
            for gn in ["A", "B", "C"]:
                if gn < group_name:
                    counter_base += len(GROUP_MATCHES.get(gn, []))

            group_doubles = doubles_by_group[group_name]

            for i, (idx_a, idx_b) in enumerate(match_pairs):
                double_a = group_doubles[idx_a]
                double_b = group_doubles[idx_b]
                match_num = counter_base + i
                match, created = Match.objects.get_or_create(
                    match_number=match_num,
                    defaults={
                        "phase": Match.PHASE_GROUP,
                        "group": group,
                        "double_1": double_a,
                        "double_2": double_b,
                        "status": Match.STATUS_PENDING,
                        "sort_order": sort_offset + i,
                    },
                )
                if created:
                    ensure_sets(match)
                    matches_created += 1

        self.stdout.write(f"{matches_created} partida(s) de grupo criada(s)")

        ensure_bracket_exists()
        bracket_count = Match.objects.filter(match_number__lt=1000).count()
        self.stdout.write(f"{bracket_count} partida(s) de bracket existem")

        total_groups = Group.objects.count()
        total_doubles = Double.objects.count()
        total_matches = Match.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTotal: {total_groups} grupo(s), "
                f"{total_doubles} dupla(s), "
                f"{total_matches} partida(s)"
            )
        )
