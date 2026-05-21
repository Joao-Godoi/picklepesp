from tournament.models import Group, Match


def get_groups_page_data():
    groups = Group.objects.prefetch_related("doubles").order_by("name")
    group_data = []
    for group in groups:
        from tournament.services import compute_group_standings

        standings = compute_group_standings(group)
        matches = (
            Match.objects.filter(
                phase=Match.PHASE_GROUP,
                group=group,
            )
            .select_related("double_1", "double_2", "winner")
            .prefetch_related("sets")
            .order_by("sort_order", "match_number")
        )
        group_data.append(
            {
                "group": group,
                "standings": standings,
                "matches": matches,
            }
        )
    return group_data


def get_playoffs_page_data():
    matches = (
        Match.objects.filter(match_number__lt=1000)
        .select_related("double_1", "double_2", "winner")
        .prefetch_related("sets")
        .order_by("sort_order", "match_number")
    )
    phases = _organize_bracket_phases(matches)
    return {"matches": matches, "phases": phases}


def get_placements_page_data():
    matches = (
        Match.objects.filter(
            phase=Match.PHASE_DISPUTE,
            match_number__lt=1000,
        )
        .select_related("double_1", "double_2", "winner")
        .prefetch_related("sets")
        .order_by("sort_order", "match_number")
    )
    phases = _organize_bracket_phases(matches)
    return {"matches": matches, "phases": phases}


PHASE_ORDER = [
    (1, "Disputa 12\u00ba ao 14\u00ba"),
    (2, "Disputa 12\u00ba ao 14\u00ba"),
    (3, "Disputa 9\u00ba ao 11\u00ba"),
    (4, "Disputa 9\u00ba ao 11\u00ba"),
    (5, "Quartas de Final"),
    (6, "Quartas de Final"),
    (7, "Quartas de Final"),
    (8, "Quartas de Final"),
    (9, "Disputa 5\u00ba ao 8\u00ba"),
    (10, "Disputa 5\u00ba ao 8\u00ba"),
    (11, "Disputa 7\u00ba e 8\u00ba"),
    (12, "Disputa 5\u00ba e 6\u00ba"),
    (13, "Semifinal"),
    (14, "Semifinal"),
    (15, "Disputa 3\u00ba e 4\u00ba"),
    (16, "Final"),
]


def _organize_bracket_phases(matches):
    seen_phases = {}
    for mn, label in PHASE_ORDER:
        if label not in seen_phases:
            seen_phases[label] = []
    for match in matches:
        label = match.phase_label
        if label not in seen_phases:
            seen_phases[label] = []
        seen_phases[label].append(match)

    phases = []
    for label in dict.fromkeys(l for _, l in PHASE_ORDER):
        if label in seen_phases and seen_phases[label]:
            phases.append(
                {
                    "phase": label,
                    "label": label,
                    "matches": seen_phases[label],
                }
            )
    return phases
