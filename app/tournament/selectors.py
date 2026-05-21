from tournament.models import Group, Match


def get_groups_page_data():
    groups = Group.objects.prefetch_related("teams").order_by("name")
    group_data = []
    for group in groups:
        from tournament.services import compute_group_standings

        standings = compute_group_standings(group)
        matches = (
            Match.objects.filter(
                bracket_type=Match.BRACKET_GROUP,
                group=group,
            )
            .select_related("team_a", "team_b", "winner")
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
        Match.objects.filter(bracket_type=Match.BRACKET_MAIN)
        .select_related("team_a", "team_b", "winner")
        .prefetch_related("sets")
        .order_by("sort_order", "match_number")
    )
    phases = _organize_bracket_phases(matches)
    return {"matches": matches, "phases": phases}


def get_placements_page_data():
    matches = (
        Match.objects.filter(bracket_type=Match.BRACKET_PLACEMENT)
        .select_related("team_a", "team_b", "winner")
        .prefetch_related("sets")
        .order_by("sort_order", "match_number")
    )
    phases = _organize_bracket_phases(matches)
    return {"matches": matches, "phases": phases}


def _organize_bracket_phases(matches):
    phase_order = [
        Match.PHASE_PLACEMENT_9_14,
        Match.PHASE_QUARTERFINAL,
        Match.PHASE_FIFTH_TO_EIGHTH,
        Match.PHASE_SEMIFINAL,
        Match.PHASE_THIRD_PLACE,
        Match.PHASE_FINAL,
    ]
    phases = []
    for phase in phase_order:
        phase_matches = [m for m in matches if m.phase == phase]
        if phase_matches:
            phases.append(
                {
                    "phase": phase,
                    "label": dict(Match.PHASE_CHOICES).get(phase, phase),
                    "matches": phase_matches,
                }
            )
    return phases
