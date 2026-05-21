from tournament.models import Group, Match, Set


QUALIFIED_POSITIONS = {"A": 3, "B": 3, "C": 2}

PLAYOFF_PHASE_ORDER = [
    (5, "Quartas de Final"),
    (6, "Quartas de Final"),
    (7, "Quartas de Final"),
    (8, "Quartas de Final"),
    (13, "Semifinal"),
    (14, "Semifinal"),
    (15, "3\u00ba e 4\u00ba Lugar"),
    (16, "Final"),
]

PLACEMENT_PHASE_ORDER = [
    (1, "Disputa 12\u00ba ao 14\u00ba"),
    (2, "Disputa 12\u00ba ao 14\u00ba"),
    (3, "Disputa 9\u00ba ao 11\u00ba"),
    (4, "Disputa 9\u00ba ao 11\u00ba"),
    (9, "Disputa 5\u00ba ao 8\u00ba"),
    (10, "Disputa 5\u00ba ao 8\u00ba"),
    (11, "Disputa 7\u00ba e 8\u00ba"),
    (12, "Disputa 5\u00ba e 6\u00ba"),
]

PHASE_ORDER = PLAYOFF_PHASE_ORDER + PLACEMENT_PHASE_ORDER


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
        qualified_count = QUALIFIED_POSITIONS.get(group.name, 2)
        group_data.append(
            {
                "group": group,
                "standings": standings,
                "matches": matches,
                "qualified_count": qualified_count,
            }
        )
    return group_data


def get_playoffs_page_data():
    playoff_numbers = [5, 6, 7, 8, 13, 14, 15, 16]
    matches = (
        Match.objects.filter(match_number__in=playoff_numbers)
        .select_related("double_1", "double_2", "winner")
        .prefetch_related("sets")
        .order_by("sort_order", "match_number")
    )
    phases = _organize_bracket_phases(matches, PLAYOFF_PHASE_ORDER)
    return {"matches": matches, "phases": phases}


def get_placements_page_data():
    placement_numbers = [1, 2, 3, 4, 9, 10, 11, 12]
    matches = (
        Match.objects.filter(match_number__in=placement_numbers)
        .select_related("double_1", "double_2", "winner")
        .prefetch_related("sets")
        .order_by("sort_order", "match_number")
    )
    phases = _organize_bracket_phases(matches, PLACEMENT_PHASE_ORDER)
    return {"matches": matches, "phases": phases}


def get_match_detail(match_number):
    match = (
        Match.objects.filter(match_number=match_number)
        .select_related("double_1", "double_2", "winner", "group")
        .prefetch_related("sets")
        .first()
    )
    return match


def get_info_page_data():
    upcoming_matches = (
        Match.objects.filter(status__in=[Match.STATUS_PENDING, Match.STATUS_IN_PROGRESS])
        .select_related("double_1", "double_2", "winner")
        .prefetch_related("sets")
        .order_by("sort_order", "match_number")[:10]
    )
    finished_count = Match.objects.filter(status=Match.STATUS_FINISHED).count()
    total_count = Match.objects.count()
    return {
        "upcoming_matches": upcoming_matches,
        "finished_count": finished_count,
        "total_count": total_count,
    }


def get_overall_standings():
    from tournament.services import compute_group_standings

    groups = Group.objects.prefetch_related("doubles").order_by("name")
    all_standings = []
    for group in groups:
        standings = compute_group_standings(group)
        qualified_count = QUALIFIED_POSITIONS.get(group.name, 2)
        for s in standings:
            s["group"] = group
            s["qualified"] = s["position"] <= qualified_count
            all_standings.append(s)

    all_standings.sort(
        key=lambda s: (
            -s["wins"],
            -s["sets_balance"],
            -s["points_balance"],
            s["double"].name,
        )
    )
    for i, s in enumerate(all_standings):
        s["overall_position"] = i + 1

    return all_standings


def get_admin_matches():
    group_matches = (
        Match.objects.filter(phase=Match.PHASE_GROUP)
        .select_related("double_1", "double_2", "winner", "group")
        .prefetch_related("sets")
        .order_by("group__name", "sort_order", "match_number")
    )
    bracket_matches = (
        Match.objects.exclude(phase=Match.PHASE_GROUP)
        .select_related("double_1", "double_2", "winner")
        .prefetch_related("sets")
        .order_by("sort_order", "match_number")
    )
    return {"group_matches": group_matches, "bracket_matches": bracket_matches}


def _organize_bracket_phases(matches, phase_order=None):
    if phase_order is None:
        phase_order = PHASE_ORDER
    seen_phases = {}
    for mn, label in phase_order:
        if label not in seen_phases:
            seen_phases[label] = []
    for match in matches:
        label = match.phase_label
        if label not in seen_phases:
            seen_phases[label] = []
        seen_phases[label].append(match)

    phases = []
    for label in dict.fromkeys(l for _, l in phase_order):
        if label in seen_phases and seen_phases[label]:
            phases.append(
                {
                    "phase": label,
                    "label": label,
                    "matches": seen_phases[label],
                }
            )
    return phases