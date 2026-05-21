import re

from django.db import transaction

from tournament.models import Double, Group, Match, Set as MatchSet


def ensure_sets(match):
    needed = match.best_of
    existing = match.sets.count()

    if existing < needed:
        for i in range(existing + 1, needed + 1):
            MatchSet.objects.create(
                match=match,
                set_number=i,
                double_1=match.double_1,
                double_2=match.double_2,
            )
    elif existing > needed:
        for s in match.sets.filter(set_number__gt=needed):
            if s.points_double_1 == 0 and s.points_double_2 == 0:
                s.delete()

    if match.double_1_id and match.double_2_id:
        match.sets.filter(
            set_number__lte=needed,
        ).update(
            double_1_id=match.double_1_id,
            double_2_id=match.double_2_id,
        )


def update_match_from_sets(match):
    sets = list(match.sets.all().order_by("set_number"))

    if not sets:
        match.status = Match.STATUS_PENDING
        match.winner_id = None
        match.save(update_fields=["status", "winner"])
        return

    for s in sets:
        new_winner_id = None
        if s.points_double_1 > s.points_double_2 and s.double_1_id:
            new_winner_id = s.double_1_id
        elif s.points_double_2 > s.points_double_1 and s.double_2_id:
            new_winner_id = s.double_2_id
        if s.winner_id != new_winner_id:
            s.winner_id = new_winner_id
            s.save(update_fields=["winner"])

    d1_wins = sum(1 for s in sets if s.winner_id and s.winner_id == match.double_1_id)
    d2_wins = sum(1 for s in sets if s.winner_id and s.winner_id == match.double_2_id)
    wins_needed = (match.best_of // 2) + 1

    if d1_wins >= wins_needed:
        match.winner_id = match.double_1_id
        match.status = Match.STATUS_FINISHED
    elif d2_wins >= wins_needed:
        match.winner_id = match.double_2_id
        match.status = Match.STATUS_FINISHED
    elif any(s.points_double_1 > 0 or s.points_double_2 > 0 for s in sets):
        match.status = Match.STATUS_IN_PROGRESS
        match.winner_id = None
    else:
        match.status = Match.STATUS_PENDING
        match.winner_id = None

    match.save(update_fields=["status", "winner"])


def determine_match_winner(match):
    sets = match.sets.all().order_by("set_number")
    if not sets.exists():
        return None
    if not match.double_1_id or not match.double_2_id:
        return None

    d1_wins = 0
    d2_wins = 0
    wins_needed = (match.best_of // 2) + 1

    for s in sets:
        if s.winner_id == match.double_1_id:
            d1_wins += 1
        elif s.winner_id == match.double_2_id:
            d2_wins += 1

    if d1_wins >= wins_needed:
        return match.double_1
    if d2_wins >= wins_needed:
        return match.double_2
    return None


def propagate_match_result(match):
    if not match.winner_id:
        return

    loser_id = (
        match.double_2_id
        if match.winner_id == match.double_1_id
        else match.double_1_id
    )

    for dependent in match.dependent_as_double_1.all():
        if dependent.source_match_1_is_winner:
            dependent.double_1_id = match.winner_id
        else:
            dependent.double_1_id = loser_id
        _update_dependent(dependent)

    for dependent in match.dependent_as_double_2.all():
        if dependent.source_match_2_is_winner:
            dependent.double_2_id = match.winner_id
        else:
            dependent.double_2_id = loser_id
        _update_dependent(dependent)


def _update_dependent(match):
    match.save(update_fields=["double_1", "double_2"])
    ensure_sets(match)


_POSITION_RE = re.compile(r"^(\d+)[\u00ba\u00b0]?\s*Grupo\s+([A-C])$", re.UNICODE)


def _resolve_position_double(source_str, standings_map):
    if not source_str:
        return None
    m = _POSITION_RE.match(source_str.strip())
    if not m:
        return None
    position = int(m.group(1))
    group_name = m.group(2)
    group_standings = standings_map.get(group_name, [])
    for entry in group_standings:
        if entry["position"] == position:
            return entry["double"]
    return None


def resolve_group_positions():
    standings_map = {}
    for group in Group.objects.all():
        standings_map[group.name] = compute_group_standings(group)

    updated = 0
    for match in Match.objects.exclude(phase=Match.PHASE_GROUP).filter(
        status__in=[Match.STATUS_PENDING, Match.STATUS_IN_PROGRESS]
    ):
        changed = False

        if not match.double_1_id and match.source_double_1_desc:
            double = _resolve_position_double(
                match.source_double_1_desc, standings_map
            )
            if double:
                match.double_1 = double
                changed = True

        if not match.double_2_id and match.source_double_2_desc:
            double = _resolve_position_double(
                match.source_double_2_desc, standings_map
            )
            if double:
                match.double_2 = double
                changed = True

        if changed:
            match.save(update_fields=["double_1", "double_2"])
            ensure_sets(match)
            updated += 1

    return updated


def _try_resolve_teams(match):
    changed = False

    if match.source_match_1_id:
        source = match.source_match_1
        if source and source.status == Match.STATUS_FINISHED and source.winner_id:
            loser_id = (
                source.double_2_id
                if source.winner_id == source.double_1_id
                else source.double_1_id
            )
            resolved_id = (
                source.winner_id
                if match.source_match_1_is_winner
                else loser_id
            )
            if match.double_1_id != resolved_id:
                match.double_1_id = resolved_id
                changed = True

    if match.source_match_2_id:
        source = match.source_match_2
        if source and source.status == Match.STATUS_FINISHED and source.winner_id:
            loser_id = (
                source.double_2_id
                if source.winner_id == source.double_1_id
                else source.double_1_id
            )
            resolved_id = (
                source.winner_id
                if match.source_match_2_is_winner
                else loser_id
            )
            if match.double_2_id != resolved_id:
                match.double_2_id = resolved_id
                changed = True

    if changed:
        match.save(update_fields=["double_1", "double_2"])
        ensure_sets(match)


def recalculate_tournament():
    with transaction.atomic():
        for match in Match.objects.filter(status=Match.STATUS_FINISHED).order_by(
            "sort_order", "match_number"
        ):
            update_match_from_sets(match)
            winner = determine_match_winner(match)
            if winner and match.winner_id != winner.pk:
                match.winner = winner
                match.save(update_fields=["winner"])
            propagate_match_result(match)

        resolve_group_positions()

        for match in Match.objects.exclude(status=Match.STATUS_FINISHED).order_by(
            "sort_order", "match_number"
        ):
            if match.source_match_1_id or match.source_match_2_id:
                _try_resolve_teams(match)

        for match in Match.objects.exclude(status=Match.STATUS_FINISHED).order_by(
            "sort_order", "match_number"
        ):
            update_match_from_sets(match)


def compute_group_standings(group):
    doubles = list(group.doubles.all())
    matches = Match.objects.filter(
        phase=Match.PHASE_GROUP,
        group=group,
        status=Match.STATUS_FINISHED,
    ).select_related("double_1", "double_2", "winner").prefetch_related("sets")

    standings = []
    for double in doubles:
        stats = {
            "double": double,
            "position": 0,
            "games": 0,
            "wins": 0,
            "losses": 0,
            "sets_won": 0,
            "sets_lost": 0,
            "sets_balance": 0,
            "points_scored": 0,
            "points_conceded": 0,
            "points_balance": 0,
        }

        for match in matches:
            if match.double_1_id != double.pk and match.double_2_id != double.pk:
                continue

            stats["games"] += 1
            is_double_1 = match.double_1_id == double.pk

            if match.winner_id == double.pk:
                stats["wins"] += 1
            else:
                stats["losses"] += 1

            for s in match.sets.all():
                if is_double_1:
                    if s.winner_id == double.pk:
                        stats["sets_won"] += 1
                    elif s.winner_id:
                        stats["sets_lost"] += 1
                    stats["points_scored"] += s.points_double_1
                    stats["points_conceded"] += s.points_double_2
                else:
                    if s.winner_id == double.pk:
                        stats["sets_won"] += 1
                    elif s.winner_id:
                        stats["sets_lost"] += 1
                    stats["points_scored"] += s.points_double_2
                    stats["points_conceded"] += s.points_double_1

        stats["sets_balance"] = stats["sets_won"] - stats["sets_lost"]
        stats["points_balance"] = stats["points_scored"] - stats["points_conceded"]
        standings.append(stats)

    standings.sort(
        key=lambda s: (-s["wins"], -s["sets_balance"], -s["points_balance"])
    )

    for i, s in enumerate(standings):
        s["position"] = i + 1

    return standings


BRACKET_MATCHES = [
    {
        "match_number": 1,
        "phase": Match.PHASE_DISPUTE,
        "best_of": 1,
        "source_double_1_desc": "5\u00ba Grupo A",
        "source_double_2_desc": "5\u00ba Grupo B",
        "final_position_loser": 14,
        "sort_order": 1,
    },
    {
        "match_number": 2,
        "phase": Match.PHASE_DISPUTE,
        "best_of": 1,
        "source_double_1_desc": "Vencedor jogo 1",
        "source_double_2_desc": "4\u00ba Grupo C",
        "source_match_1_number": 1,
        "source_match_1_is_winner": True,
        "final_position_loser": 13,
        "final_position_winner": 12,
        "sort_order": 2,
    },
    {
        "match_number": 3,
        "phase": Match.PHASE_DISPUTE,
        "best_of": 1,
        "source_double_1_desc": "4\u00ba Grupo A",
        "source_double_2_desc": "4\u00ba Grupo B",
        "final_position_loser": 11,
        "sort_order": 3,
    },
    {
        "match_number": 4,
        "phase": Match.PHASE_DISPUTE,
        "best_of": 1,
        "source_double_1_desc": "Vencedor jogo 3",
        "source_double_2_desc": "3\u00ba Grupo C",
        "source_match_1_number": 3,
        "source_match_1_is_winner": True,
        "final_position_loser": 10,
        "final_position_winner": 9,
        "sort_order": 4,
    },
    {
        "match_number": 5,
        "phase": Match.PHASE_SEMIFINAL,
        "best_of": 3,
        "source_double_1_desc": "1\u00ba Grupo A",
        "source_double_2_desc": "3\u00ba Grupo B",
        "sort_order": 5,
    },
    {
        "match_number": 6,
        "phase": Match.PHASE_SEMIFINAL,
        "best_of": 3,
        "source_double_1_desc": "1\u00ba Grupo C",
        "source_double_2_desc": "2\u00ba Grupo A",
        "sort_order": 6,
    },
    {
        "match_number": 7,
        "phase": Match.PHASE_SEMIFINAL,
        "best_of": 3,
        "source_double_1_desc": "1\u00ba Grupo B",
        "source_double_2_desc": "3\u00ba Grupo A",
        "sort_order": 7,
    },
    {
        "match_number": 8,
        "phase": Match.PHASE_SEMIFINAL,
        "best_of": 3,
        "source_double_1_desc": "2\u00ba Grupo B",
        "source_double_2_desc": "2\u00ba Grupo C",
        "sort_order": 8,
    },
    {
        "match_number": 9,
        "phase": Match.PHASE_DISPUTE,
        "best_of": 1,
        "source_double_1_desc": "Perdedor jogo 5",
        "source_double_2_desc": "Perdedor jogo 6",
        "source_match_1_number": 5,
        "source_match_1_is_winner": False,
        "source_match_2_number": 6,
        "source_match_2_is_winner": False,
        "sort_order": 9,
    },
    {
        "match_number": 10,
        "phase": Match.PHASE_DISPUTE,
        "best_of": 1,
        "source_double_1_desc": "Perdedor jogo 7",
        "source_double_2_desc": "Perdedor jogo 8",
        "source_match_1_number": 7,
        "source_match_1_is_winner": False,
        "source_match_2_number": 8,
        "source_match_2_is_winner": False,
        "sort_order": 10,
    },
    {
        "match_number": 11,
        "phase": Match.PHASE_DISPUTE,
        "best_of": 1,
        "source_double_1_desc": "Perdedor jogo 9",
        "source_double_2_desc": "Perdedor jogo 10",
        "source_match_1_number": 9,
        "source_match_1_is_winner": False,
        "source_match_2_number": 10,
        "source_match_2_is_winner": False,
        "final_position_winner": 7,
        "final_position_loser": 8,
        "sort_order": 11,
    },
    {
        "match_number": 12,
        "phase": Match.PHASE_DISPUTE,
        "best_of": 1,
        "source_double_1_desc": "Vencedor jogo 9",
        "source_double_2_desc": "Vencedor jogo 10",
        "source_match_1_number": 9,
        "source_match_1_is_winner": True,
        "source_match_2_number": 10,
        "source_match_2_is_winner": True,
        "final_position_winner": 5,
        "final_position_loser": 6,
        "sort_order": 12,
    },
    {
        "match_number": 13,
        "phase": Match.PHASE_SEMIFINAL,
        "best_of": 3,
        "source_double_1_desc": "Vencedor jogo 5",
        "source_double_2_desc": "Vencedor jogo 6",
        "source_match_1_number": 5,
        "source_match_1_is_winner": True,
        "source_match_2_number": 6,
        "source_match_2_is_winner": True,
        "sort_order": 13,
    },
    {
        "match_number": 14,
        "phase": Match.PHASE_SEMIFINAL,
        "best_of": 3,
        "source_double_1_desc": "Vencedor jogo 7",
        "source_double_2_desc": "Vencedor jogo 8",
        "source_match_1_number": 7,
        "source_match_1_is_winner": True,
        "source_match_2_number": 8,
        "source_match_2_is_winner": True,
        "sort_order": 14,
    },
    {
        "match_number": 15,
        "phase": Match.PHASE_DISPUTE,
        "best_of": 1,
        "source_double_1_desc": "Perdedor jogo 13",
        "source_double_2_desc": "Perdedor jogo 14",
        "source_match_1_number": 13,
        "source_match_1_is_winner": False,
        "source_match_2_number": 14,
        "source_match_2_is_winner": False,
        "final_position_winner": 3,
        "final_position_loser": 4,
        "sort_order": 15,
    },
    {
        "match_number": 16,
        "phase": Match.PHASE_FINAL,
        "best_of": 3,
        "source_double_1_desc": "Vencedor jogo 13",
        "source_double_2_desc": "Vencedor jogo 14",
        "source_match_1_number": 13,
        "source_match_1_is_winner": True,
        "source_match_2_number": 14,
        "source_match_2_is_winner": True,
        "final_position_winner": 1,
        "final_position_loser": 2,
        "sort_order": 16,
    },
]


def ensure_bracket_exists():
    for match_data in BRACKET_MATCHES:
        match, created = Match.objects.get_or_create(
            match_number=match_data["match_number"],
            defaults={
                "phase": match_data["phase"],
                "source_double_1_desc": match_data.get("source_double_1_desc", ""),
                "source_double_2_desc": match_data.get("source_double_2_desc", ""),
                "final_position_winner": match_data.get("final_position_winner"),
                "final_position_loser": match_data.get("final_position_loser"),
                "sort_order": match_data["sort_order"],
                "status": Match.STATUS_PENDING,
            },
        )
        if created:
            ensure_sets(match)

    _link_source_matches()


def _link_source_matches():
    for match_data in BRACKET_MATCHES:
        match = Match.objects.filter(
            match_number=match_data["match_number"],
        ).first()
        if not match:
            continue

        updated = False

        if "source_match_1_number" in match_data:
            source = Match.objects.filter(
                match_number=match_data["source_match_1_number"],
            ).first()
            if source:
                match.source_match_1 = source
                match.source_match_1_is_winner = match_data.get(
                    "source_match_1_is_winner"
                )
                updated = True

        if "source_match_2_number" in match_data:
            source = Match.objects.filter(
                match_number=match_data["source_match_2_number"],
            ).first()
            if source:
                match.source_match_2 = source
                match.source_match_2_is_winner = match_data.get(
                    "source_match_2_is_winner"
                )
                updated = True

        if updated:
            match.save()
