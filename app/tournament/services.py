import re

from django.core.exceptions import ValidationError
from django.db import transaction

from tournament.models import Group, Match


def determine_match_winner(match):
    sets = match.sets.all().order_by("set_number")
    if not sets.exists():
        return None
    if not match.team_a_id or not match.team_b_id:
        return None

    team_a_wins = 0
    team_b_wins = 0
    wins_needed = (match.best_of // 2) + 1

    for s in sets:
        if s.team_a_points > s.team_b_points:
            team_a_wins += 1
        elif s.team_b_points > s.team_a_points:
            team_b_wins += 1

    if team_a_wins >= wins_needed:
        return match.team_a
    if team_b_wins >= wins_needed:
        return match.team_b
    return None


def validate_match_sets(match):
    errors = []
    sets = list(match.sets.all().order_by("set_number"))

    if not sets:
        if match.status == Match.STATUS_FINISHED:
            errors.append("Partida finalizada deve possuir sets.")
        return errors

    for i, s in enumerate(sets, 1):
        if s.set_number != i:
            errors.append(
                f"Sets devem ser numerados sequencialmente a partir de 1. "
                f"Esperado {i}, encontrado {s.set_number}."
            )

    for s in sets:
        if s.team_a_points == s.team_b_points:
            errors.append(f"Set {s.set_number} nao pode terminar empatado.")

    for s in sets:
        if s.team_a_points < 11 and s.team_b_points < 11:
            errors.append(
                f"Set {s.set_number}: pelo menos um lado deve atingir 11 pontos."
            )

    for s in sets:
        if s.team_a_points > 11 or s.team_b_points > 11:
            errors.append(
                f"Set {s.set_number}: pontuacao maxima por set e 11 pontos."
            )

    if len(sets) > match.best_of:
        errors.append(
            f"Partida melhor de {match.best_of} permite no maximo "
            f"{match.best_of} set(s)."
        )

    if match.status == Match.STATUS_FINISHED:
        wins_needed = (match.best_of // 2) + 1
        team_a_wins = sum(
            1 for s in sets if s.team_a_points > s.team_b_points
        )
        team_b_wins = sum(
            1 for s in sets if s.team_b_points > s.team_a_points
        )

        if team_a_wins < wins_needed and team_b_wins < wins_needed:
            errors.append(
                f"Partida finalizada requer {wins_needed} set(s) vencido(s) por uma dupla."
            )

        winner = determine_match_winner(match)
        if winner and match.winner_id and winner.pk != match.winner_id:
            errors.append(
                f"Vencedor inconsistente com os sets. Vencedor calculado: {winner}."
            )

        if not match.team_a_id or not match.team_b_id:
            errors.append("Partida finalizada deve ter ambas as duplas definidas.")

    return errors


def validate_match_for_finish(match):
    errors = []

    if not match.team_a_id or not match.team_b_id:
        errors.append("Ambas as duplas devem estar definidas para finalizar.")
    if match.team_a_id and match.team_b_id and match.team_a_id == match.team_b_id:
        errors.append("Uma dupla nao pode enfrentar a si mesma.")

    sets_errors = validate_match_sets(match)
    errors.extend(sets_errors)

    if not errors:
        winner = determine_match_winner(match)
        if not winner:
            errors.append(
                "Nao foi possivel determinar o vencedor a partir dos sets."
            )

    if errors:
        raise ValidationError(errors)

    return winner


def finalize_match(match):
    winner = validate_match_for_finish(match)
    match.winner = winner
    match.status = Match.STATUS_FINISHED
    match.save(update_fields=["winner", "status", "updated_at"])
    propagate_match_result(match)
    return match


def propagate_match_result(match):
    if not match.winner_id:
        return

    loser_id = match.team_b_id if match.winner_id == match.team_a_id else match.team_a_id

    for dependent in match.dependent_as_team_a.all():
        if dependent.source_match_a_is_winner:
            dependent.team_a_id = match.winner_id
        else:
            dependent.team_a_id = loser_id
        _update_dependent_status(dependent)

    for dependent in match.dependent_as_team_b.all():
        if dependent.source_match_b_is_winner:
            dependent.team_b_id = match.winner_id
        else:
            dependent.team_b_id = loser_id
        _update_dependent_status(dependent)


def _update_dependent_status(match):
    if match.team_a_id and match.team_b_id:
        if match.status in (Match.STATUS_PENDING, Match.STATUS_BLOCKED):
            match.status = Match.STATUS_READY
    match.save(update_fields=["team_a", "team_b", "status", "updated_at"])


_POSITION_RE = re.compile(r"^(\d+).+\s+Grupo\s+([A-C])$", re.UNICODE)


def _resolve_position_team(source_str, standings_map):
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
            return entry["team"]
    return None


def resolve_group_positions():
    standings_map = {}
    for group in Group.objects.all():
        standings_map[group.name] = compute_group_standings(group)

    updated = 0
    for match in Match.objects.exclude(bracket_type=Match.BRACKET_GROUP).filter(
        status__in=[Match.STATUS_BLOCKED, Match.STATUS_PENDING, Match.STATUS_READY]
    ):
        changed = False

        if not match.team_a_id and match.source_team_a:
            team = _resolve_position_team(match.source_team_a, standings_map)
            if team:
                match.team_a = team
                changed = True

        if not match.team_b_id and match.source_team_b:
            team = _resolve_position_team(match.source_team_b, standings_map)
            if team:
                match.team_b = team
                changed = True

        if changed:
            _update_dependent_status(match)
            updated += 1

    return updated


def recalculate_tournament():
    with transaction.atomic():
        for match in Match.objects.filter(status=Match.STATUS_FINISHED).order_by(
            "sort_order", "match_number"
        ):
            winner = determine_match_winner(match)
            if winner and match.winner_id != winner.pk:
                match.winner = winner
                match.save(update_fields=["winner", "updated_at"])
            propagate_match_result(match)

        resolve_group_positions()

        for match in Match.objects.exclude(status=Match.STATUS_FINISHED).order_by(
            "sort_order", "match_number"
        ):
            if match.source_match_a_id or match.source_match_b_id:
                _try_resolve_teams(match)


def _try_resolve_teams(match):
    changed = False

    if match.source_match_a_id:
        source = match.source_match_a
        if source and source.status == Match.STATUS_FINISHED and source.winner_id:
            loser_id = (
                source.team_b_id
                if source.winner_id == source.team_a_id
                else source.team_a_id
            )
            resolved_id = source.winner_id if match.source_match_a_is_winner else loser_id
            if match.team_a_id != resolved_id:
                match.team_a_id = resolved_id
                changed = True

    if match.source_match_b_id:
        source = match.source_match_b
        if source and source.status == Match.STATUS_FINISHED and source.winner_id:
            loser_id = (
                source.team_b_id
                if source.winner_id == source.team_a_id
                else source.team_a_id
            )
            resolved_id = source.winner_id if match.source_match_b_is_winner else loser_id
            if match.team_b_id != resolved_id:
                match.team_b_id = resolved_id
                changed = True

    if changed:
        _update_dependent_status(match)


def compute_group_standings(group):
    teams = list(group.teams.all())
    matches = Match.objects.filter(
        bracket_type=Match.BRACKET_GROUP,
        group=group,
        status=Match.STATUS_FINISHED,
    ).select_related("team_a", "team_b", "winner").prefetch_related("sets")

    standings = []
    for team in teams:
        stats = {
            "team": team,
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
            if match.team_a_id != team.pk and match.team_b_id != team.pk:
                continue

            stats["games"] += 1
            is_team_a = match.team_a_id == team.pk

            if match.winner_id == team.pk:
                stats["wins"] += 1
            else:
                stats["losses"] += 1

            for s in match.sets.all():
                if is_team_a:
                    if s.team_a_points > s.team_b_points:
                        stats["sets_won"] += 1
                    else:
                        stats["sets_lost"] += 1
                    stats["points_scored"] += s.team_a_points
                    stats["points_conceded"] += s.team_b_points
                else:
                    if s.team_b_points > s.team_a_points:
                        stats["sets_won"] += 1
                    else:
                        stats["sets_lost"] += 1
                    stats["points_scored"] += s.team_b_points
                    stats["points_conceded"] += s.team_a_points

        stats["sets_balance"] = stats["sets_won"] - stats["sets_lost"]
        stats["points_balance"] = stats["points_scored"] - stats["points_conceded"]
        standings.append(stats)

    standings.sort(
        key=lambda s: (-s["wins"], -s["sets_balance"], -s["points_balance"])
    )

    for i, s in enumerate(standings):
        s["position"] = i + 1

    return standings
