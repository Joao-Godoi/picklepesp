from django.test import TestCase
from django.core.exceptions import ValidationError

from tournament.models import Group, Team, Match, MatchSet
from tournament.services import (
    determine_match_winner,
    validate_match_sets,
    validate_match_for_finish,
    finalize_match,
    compute_group_standings,
)


class MatchSetValidationTest(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name="A")
        self.team_a = Team.objects.create(
            player1_name="Player 1", player2_name="Player 2", group=self.group
        )
        self.team_b = Team.objects.create(
            player1_name="Player 3", player2_name="Player 4", group=self.group
        )
        self.match = Match.objects.create(
            phase=Match.PHASE_GROUP,
            match_number=1000,
            bracket_type=Match.BRACKET_GROUP,
            group=self.group,
            team_a=self.team_a,
            team_b=self.team_b,
            status=Match.STATUS_READY,
            best_of=3,
            sort_order=1,
        )

    def test_tied_set_raises_error(self):
        match_set = MatchSet(
            match=self.match, set_number=1, team_a_points=11, team_b_points=11
        )
        with self.assertRaises(ValidationError) as ctx:
            match_set.clean()
        self.assertIn("empatado", str(ctx.exception))

    def test_set_both_below_11_raises_error(self):
        match_set = MatchSet(
            match=self.match, set_number=1, team_a_points=10, team_b_points=8
        )
        with self.assertRaises(ValidationError) as ctx:
            match_set.clean()
        self.assertIn("11 pontos", str(ctx.exception))

    def test_set_above_11_raises_error(self):
        match_set = MatchSet(
            match=self.match, set_number=1, team_a_points=12, team_b_points=10
        )
        with self.assertRaises(ValidationError) as ctx:
            match_set.clean()
        self.assertIn("11 pontos", str(ctx.exception))

    def test_both_sides_above_11_raises_error(self):
        match_set = MatchSet(
            match=self.match, set_number=1, team_a_points=13, team_b_points=12
        )
        with self.assertRaises(ValidationError) as ctx:
            match_set.clean()
        self.assertIn("11 pontos", str(ctx.exception))

    def test_valid_set_11_x_9(self):
        match_set = MatchSet(
            match=self.match, set_number=1, team_a_points=11, team_b_points=9
        )
        match_set.clean()

    def test_valid_set_11_x_0(self):
        match_set = MatchSet(
            match=self.match, set_number=1, team_a_points=11, team_b_points=0
        )
        match_set.clean()

    def test_too_many_sets_for_best_of_3(self):
        MatchSet.objects.create(
            match=self.match, set_number=1, team_a_points=11, team_b_points=9
        )
        MatchSet.objects.create(
            match=self.match, set_number=2, team_a_points=11, team_b_points=9
        )
        MatchSet.objects.create(
            match=self.match, set_number=3, team_a_points=11, team_b_points=9
        )
        fourth = MatchSet(
            match=self.match, set_number=4, team_a_points=11, team_b_points=9
        )
        with self.assertRaises(ValidationError) as ctx:
            fourth.clean()
        self.assertIn("no maximo", str(ctx.exception))

    def test_too_many_sets_for_best_of_1(self):
        self.match.best_of = 1
        self.match.save()
        MatchSet.objects.create(
            match=self.match, set_number=1, team_a_points=11, team_b_points=9
        )
        second = MatchSet(
            match=self.match, set_number=2, team_a_points=11, team_b_points=9
        )
        with self.assertRaises(ValidationError) as ctx:
            second.clean()
        self.assertIn("no maximo", str(ctx.exception))

    def test_set_number_out_of_range(self):
        match_set = MatchSet(
            match=self.match, set_number=0, team_a_points=11, team_b_points=9
        )
        with self.assertRaises(ValidationError) as ctx:
            match_set.clean()
        self.assertIn("entre 1 e", str(ctx.exception))

    def test_set_number_exceeds_best_of(self):
        match_set = MatchSet(
            match=self.match, set_number=4, team_a_points=11, team_b_points=9
        )
        with self.assertRaises(ValidationError) as ctx:
            match_set.clean()
        self.assertIn("entre 1 e 3", str(ctx.exception))


class MatchValidationTest(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name="A")
        self.team_a = Team.objects.create(
            player1_name="Player 1", player2_name="Player 2", group=self.group
        )
        self.team_b = Team.objects.create(
            player1_name="Player 3", player2_name="Player 4", group=self.group
        )

    def test_finished_match_without_teams_raises_error(self):
        match = Match(
            phase=Match.PHASE_GROUP,
            match_number=1000,
            bracket_type=Match.BRACKET_GROUP,
            status=Match.STATUS_FINISHED,
            best_of=3,
            sort_order=1,
        )
        with self.assertRaises(ValidationError) as ctx:
            match.clean()
        self.assertIn("obrigatorio", str(ctx.exception))

    def test_finished_match_without_winner_raises_error(self):
        match = Match(
            phase=Match.PHASE_GROUP,
            match_number=1000,
            bracket_type=Match.BRACKET_GROUP,
            team_a=self.team_a,
            team_b=self.team_b,
            status=Match.STATUS_FINISHED,
            best_of=3,
            sort_order=1,
        )
        with self.assertRaises(ValidationError) as ctx:
            match.clean()
        self.assertIn("Vencedor", str(ctx.exception))

    def test_winner_not_in_match_raises_error(self):
        team_c = Team.objects.create(
            player1_name="Player 5", player2_name="Player 6", group=self.group
        )
        match = Match(
            phase=Match.PHASE_GROUP,
            match_number=1000,
            bracket_type=Match.BRACKET_GROUP,
            team_a=self.team_a,
            team_b=self.team_b,
            winner=team_c,
            status=Match.STATUS_FINISHED,
            best_of=3,
            sort_order=1,
        )
        with self.assertRaises(ValidationError) as ctx:
            match.clean()
        self.assertIn("Time A ou Time B", str(ctx.exception))

    def test_same_team_raises_error(self):
        match = Match(
            phase=Match.PHASE_GROUP,
            match_number=1000,
            bracket_type=Match.BRACKET_GROUP,
            team_a=self.team_a,
            team_b=self.team_a,
            status=Match.STATUS_PENDING,
            best_of=3,
            sort_order=1,
        )
        with self.assertRaises(ValidationError) as ctx:
            match.clean()
        self.assertIn("diferente", str(ctx.exception))

    def test_invalid_best_of_raises_error(self):
        match = Match(
            phase=Match.PHASE_GROUP,
            match_number=1000,
            bracket_type=Match.BRACKET_GROUP,
            team_a=self.team_a,
            team_b=self.team_b,
            status=Match.STATUS_PENDING,
            best_of=5,
            sort_order=1,
        )
        with self.assertRaises(ValidationError) as ctx:
            match.clean()
        self.assertIn("1 ou 3", str(ctx.exception))

    def test_ready_status_requires_both_teams(self):
        match = Match(
            phase=Match.PHASE_GROUP,
            match_number=1000,
            bracket_type=Match.BRACKET_GROUP,
            team_a=self.team_a,
            status=Match.STATUS_READY,
            best_of=3,
            sort_order=1,
        )
        with self.assertRaises(ValidationError) as ctx:
            match.clean()
        self.assertIn("obrigatorio", str(ctx.exception))

    def test_valid_pending_match(self):
        match = Match(
            phase=Match.PHASE_GROUP,
            match_number=1000,
            bracket_type=Match.BRACKET_GROUP,
            team_a=self.team_a,
            team_b=self.team_b,
            status=Match.STATUS_READY,
            best_of=3,
            sort_order=1,
        )
        match.clean()

    def test_pending_match_without_teams_is_valid(self):
        match = Match(
            phase=Match.PHASE_QUARTERFINAL,
            match_number=5,
            bracket_type=Match.BRACKET_MAIN,
            status=Match.STATUS_BLOCKED,
            best_of=3,
            sort_order=5,
        )
        match.clean()


class DetermineWinnerTest(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name="A")
        self.team_a = Team.objects.create(
            player1_name="Player 1", player2_name="Player 2", group=self.group
        )
        self.team_b = Team.objects.create(
            player1_name="Player 3", player2_name="Player 4", group=self.group
        )
        self.match = Match.objects.create(
            phase=Match.PHASE_GROUP,
            match_number=1000,
            bracket_type=Match.BRACKET_GROUP,
            group=self.group,
            team_a=self.team_a,
            team_b=self.team_b,
            status=Match.STATUS_READY,
            best_of=3,
            sort_order=1,
        )

    def test_no_sets_returns_none(self):
        self.assertIsNone(determine_match_winner(self.match))

    def test_team_a_wins_2_0(self):
        MatchSet.objects.create(
            match=self.match, set_number=1, team_a_points=11, team_b_points=5
        )
        MatchSet.objects.create(
            match=self.match, set_number=2, team_a_points=11, team_b_points=7
        )
        self.assertEqual(determine_match_winner(self.match), self.team_a)

    def test_team_b_wins_2_1(self):
        MatchSet.objects.create(
            match=self.match, set_number=1, team_a_points=5, team_b_points=11
        )
        MatchSet.objects.create(
            match=self.match, set_number=2, team_a_points=11, team_b_points=9
        )
        MatchSet.objects.create(
            match=self.match, set_number=3, team_a_points=8, team_b_points=11
        )
        self.assertEqual(determine_match_winner(self.match), self.team_b)

    def test_incomplete_match_returns_none(self):
        MatchSet.objects.create(
            match=self.match, set_number=1, team_a_points=11, team_b_points=5
        )
        self.assertIsNone(determine_match_winner(self.match))

    def test_best_of_1_winner(self):
        match = Match.objects.create(
            phase=Match.PHASE_PLACEMENT_9_14,
            match_number=1,
            bracket_type=Match.BRACKET_PLACEMENT,
            team_a=self.team_a,
            team_b=self.team_b,
            status=Match.STATUS_READY,
            best_of=1,
            sort_order=1,
        )
        MatchSet.objects.create(
            match=match, set_number=1, team_a_points=11, team_b_points=8
        )
        self.assertEqual(determine_match_winner(match), self.team_a)

    def test_best_of_1_loser(self):
        match = Match.objects.create(
            phase=Match.PHASE_PLACEMENT_9_14,
            match_number=1,
            bracket_type=Match.BRACKET_PLACEMENT,
            team_a=self.team_a,
            team_b=self.team_b,
            status=Match.STATUS_READY,
            best_of=1,
            sort_order=1,
        )
        MatchSet.objects.create(
            match=match, set_number=1, team_a_points=6, team_b_points=11
        )
        self.assertEqual(determine_match_winner(match), self.team_b)


class ValidateMatchSetsTest(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name="A")
        self.team_a = Team.objects.create(
            player1_name="Player 1", player2_name="Player 2", group=self.group
        )
        self.team_b = Team.objects.create(
            player1_name="Player 3", player2_name="Player 4", group=self.group
        )

    def test_valid_finished_match_no_errors(self):
        match = Match.objects.create(
            phase=Match.PHASE_GROUP,
            match_number=1000,
            bracket_type=Match.BRACKET_GROUP,
            group=self.group,
            team_a=self.team_a,
            team_b=self.team_b,
            status=Match.STATUS_FINISHED,
            best_of=3,
            sort_order=1,
        )
        MatchSet.objects.create(
            match=match, set_number=1, team_a_points=11, team_b_points=5
        )
        MatchSet.objects.create(
            match=match, set_number=2, team_a_points=11, team_b_points=7
        )
        match.winner = self.team_a
        match.save()
        errors = validate_match_sets(match)
        self.assertEqual(len(errors), 0)

    def test_finished_match_without_enough_set_wins(self):
        match = Match.objects.create(
            phase=Match.PHASE_GROUP,
            match_number=1000,
            bracket_type=Match.BRACKET_GROUP,
            group=self.group,
            team_a=self.team_a,
            team_b=self.team_b,
            status=Match.STATUS_FINISHED,
            best_of=3,
            sort_order=1,
        )
        MatchSet.objects.create(
            match=match, set_number=1, team_a_points=11, team_b_points=5
        )
        MatchSet.objects.create(
            match=match, set_number=2, team_a_points=9, team_b_points=11
        )
        errors = validate_match_sets(match)
        self.assertTrue(any("set(s) vencido(s)" in e for e in errors))

    def test_finished_match_without_sets(self):
        match = Match.objects.create(
            phase=Match.PHASE_GROUP,
            match_number=1000,
            bracket_type=Match.BRACKET_GROUP,
            group=self.group,
            team_a=self.team_a,
            team_b=self.team_b,
            status=Match.STATUS_FINISHED,
            best_of=3,
            sort_order=1,
        )
        errors = validate_match_sets(match)
        self.assertTrue(any("sets" in e for e in errors))

    def test_non_sequential_set_numbers(self):
        match = Match.objects.create(
            phase=Match.PHASE_GROUP,
            match_number=1000,
            bracket_type=Match.BRACKET_GROUP,
            group=self.group,
            team_a=self.team_a,
            team_b=self.team_b,
            status=Match.STATUS_READY,
            best_of=3,
            sort_order=1,
        )
        MatchSet.objects.create(
            match=match, set_number=1, team_a_points=11, team_b_points=5
        )
        MatchSet.objects.create(
            match=match, set_number=3, team_a_points=11, team_b_points=7
        )
        errors = validate_match_sets(match)
        self.assertTrue(any("sequencialmente" in e for e in errors))

    def test_winner_inconsistent_with_sets(self):
        match = Match.objects.create(
            phase=Match.PHASE_GROUP,
            match_number=1000,
            bracket_type=Match.BRACKET_GROUP,
            group=self.group,
            team_a=self.team_a,
            team_b=self.team_b,
            winner=self.team_b,
            status=Match.STATUS_FINISHED,
            best_of=3,
            sort_order=1,
        )
        MatchSet.objects.create(
            match=match, set_number=1, team_a_points=11, team_b_points=5
        )
        MatchSet.objects.create(
            match=match, set_number=2, team_a_points=11, team_b_points=7
        )
        errors = validate_match_sets(match)
        self.assertTrue(any("inconsistente" in e for e in errors))


class FinalizeMatchTest(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name="A")
        self.team_a = Team.objects.create(
            player1_name="Player 1", player2_name="Player 2", group=self.group
        )
        self.team_b = Team.objects.create(
            player1_name="Player 3", player2_name="Player 4", group=self.group
        )

    def test_finalize_valid_match(self):
        match = Match.objects.create(
            phase=Match.PHASE_GROUP,
            match_number=1000,
            bracket_type=Match.BRACKET_GROUP,
            group=self.group,
            team_a=self.team_a,
            team_b=self.team_b,
            status=Match.STATUS_READY,
            best_of=3,
            sort_order=1,
        )
        MatchSet.objects.create(
            match=match, set_number=1, team_a_points=11, team_b_points=5
        )
        MatchSet.objects.create(
            match=match, set_number=2, team_a_points=11, team_b_points=7
        )

        finalize_match(match)
        match.refresh_from_db()
        self.assertEqual(match.status, Match.STATUS_FINISHED)
        self.assertEqual(match.winner, self.team_a)

    def test_finalize_invalid_match_raises_error(self):
        match = Match.objects.create(
            phase=Match.PHASE_GROUP,
            match_number=1000,
            bracket_type=Match.BRACKET_GROUP,
            group=self.group,
            team_a=self.team_a,
            team_b=self.team_b,
            status=Match.STATUS_READY,
            best_of=3,
            sort_order=1,
        )
        MatchSet.objects.create(
            match=match, set_number=1, team_a_points=5, team_b_points=11
        )

        with self.assertRaises(ValidationError):
            finalize_match(match)

    def test_finalize_match_without_teams_raises_error(self):
        match = Match.objects.create(
            phase=Match.PHASE_QUARTERFINAL,
            match_number=5,
            bracket_type=Match.BRACKET_MAIN,
            status=Match.STATUS_BLOCKED,
            best_of=3,
            sort_order=5,
        )

        with self.assertRaises(ValidationError):
            finalize_match(match)

    def test_finalize_best_of_1_match(self):
        match = Match.objects.create(
            phase=Match.PHASE_PLACEMENT_9_14,
            match_number=1,
            bracket_type=Match.BRACKET_PLACEMENT,
            team_a=self.team_a,
            team_b=self.team_b,
            status=Match.STATUS_READY,
            best_of=1,
            sort_order=1,
        )
        MatchSet.objects.create(
            match=match, set_number=1, team_a_points=11, team_b_points=8
        )

        finalize_match(match)
        match.refresh_from_db()
        self.assertEqual(match.status, Match.STATUS_FINISHED)
        self.assertEqual(match.winner, self.team_a)


class GroupStandingsTest(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name="A")
        self.team_a = Team.objects.create(
            player1_name="Arthur", player2_name="Flavio", group=self.group
        )
        self.team_b = Team.objects.create(
            player1_name="Rogerio", player2_name="Ana", group=self.group
        )
        self.team_c = Team.objects.create(
            player1_name="Jonas", player2_name="Valmir", group=self.group
        )

    def _create_finished_match(self, team_a, team_b, sets_data):
        match = Match.objects.create(
            phase=Match.PHASE_GROUP,
            match_number=1000 + Match.objects.filter(
                bracket_type=Match.BRACKET_GROUP
            ).count(),
            bracket_type=Match.BRACKET_GROUP,
            group=self.group,
            team_a=team_a,
            team_b=team_b,
            status=Match.STATUS_FINISHED,
            best_of=3,
            sort_order=0,
        )
        for i, (a_pts, b_pts) in enumerate(sets_data, 1):
            MatchSet.objects.create(
                match=match,
                set_number=i,
                team_a_points=a_pts,
                team_b_points=b_pts,
            )
        match.winner = determine_match_winner(match)
        match.save()
        return match

    def test_empty_group_standings(self):
        standings = compute_group_standings(self.group)
        self.assertEqual(len(standings), 3)
        for s in standings:
            self.assertEqual(s["wins"], 0)
            self.assertEqual(s["games"], 0)
            self.assertEqual(s["sets_balance"], 0)
            self.assertEqual(s["points_balance"], 0)

    def test_standings_order_by_wins(self):
        self._create_finished_match(self.team_a, self.team_b, [(11, 5), (11, 7)])
        self._create_finished_match(self.team_a, self.team_c, [(11, 9), (11, 8)])
        self._create_finished_match(self.team_b, self.team_c, [(11, 5), (11, 6)])

        standings = compute_group_standings(self.group)
        self.assertEqual(standings[0]["team"], self.team_a)
        self.assertEqual(standings[0]["wins"], 2)
        self.assertEqual(standings[1]["team"], self.team_b)
        self.assertEqual(standings[1]["wins"], 1)
        self.assertEqual(standings[2]["team"], self.team_c)
        self.assertEqual(standings[2]["wins"], 0)

    def test_tiebreaker_by_set_balance(self):
        self._create_finished_match(self.team_a, self.team_b, [(11, 5), (9, 11), (11, 7)])
        self._create_finished_match(self.team_b, self.team_c, [(11, 7), (11, 9)])
        self._create_finished_match(self.team_c, self.team_a, [(9, 11), (11, 5), (11, 8)])

        standings = compute_group_standings(self.group)
        self.assertEqual(standings[0]["team"], self.team_b)
        self.assertEqual(standings[0]["wins"], 1)
        self.assertEqual(standings[0]["sets_balance"], 1)
        self.assertEqual(standings[1]["team"], self.team_a)
        self.assertEqual(standings[1]["wins"], 1)
        self.assertEqual(standings[1]["sets_balance"], 0)
        self.assertEqual(standings[2]["team"], self.team_c)
        self.assertEqual(standings[2]["wins"], 1)
        self.assertEqual(standings[2]["sets_balance"], -1)

    def test_tiebreaker_by_point_balance(self):
        self._create_finished_match(self.team_a, self.team_b, [(11, 9), (11, 9)])
        self._create_finished_match(self.team_b, self.team_c, [(11, 5), (11, 5)])
        self._create_finished_match(self.team_c, self.team_a, [(11, 9), (11, 9)])

        standings = compute_group_standings(self.group)
        self.assertEqual(standings[0]["team"], self.team_b)
        self.assertEqual(standings[0]["points_balance"], 8)
        self.assertEqual(standings[1]["team"], self.team_a)
        self.assertEqual(standings[1]["points_balance"], 0)
        self.assertEqual(standings[2]["team"], self.team_c)
        self.assertEqual(standings[2]["points_balance"], -8)

    def test_persistent_tie_stable_order(self):
        self._create_finished_match(self.team_a, self.team_b, [(11, 5), (5, 11), (11, 5)])
        self._create_finished_match(self.team_b, self.team_c, [(11, 5), (5, 11), (11, 5)])
        self._create_finished_match(self.team_a, self.team_c, [(5, 11), (11, 5), (5, 11)])

        standings = compute_group_standings(self.group)
        positions = [s["position"] for s in standings]
        self.assertEqual(positions, [1, 2, 3])
        for s in standings:
            self.assertEqual(s["wins"], 1)
            self.assertEqual(s["sets_balance"], 0)
            self.assertEqual(s["points_balance"], 0)

    def test_games_count(self):
        self._create_finished_match(self.team_a, self.team_b, [(11, 5), (11, 7)])
        self._create_finished_match(self.team_a, self.team_c, [(11, 9), (11, 8)])

        standings = compute_group_standings(self.group)
        team_a_stats = next(s for s in standings if s["team"] == self.team_a)
        self.assertEqual(team_a_stats["games"], 2)
        self.assertEqual(team_a_stats["wins"], 2)
        self.assertEqual(team_a_stats["losses"], 0)

    def test_sets_and_points_calculation(self):
        self._create_finished_match(self.team_a, self.team_b, [(11, 5), (11, 7)])

        standings = compute_group_standings(self.group)
        team_a_stats = next(s for s in standings if s["team"] == self.team_a)
        self.assertEqual(team_a_stats["sets_won"], 2)
        self.assertEqual(team_a_stats["sets_lost"], 0)
        self.assertEqual(team_a_stats["sets_balance"], 2)
        self.assertEqual(team_a_stats["points_scored"], 22)
        self.assertEqual(team_a_stats["points_conceded"], 12)
        self.assertEqual(team_a_stats["points_balance"], 10)

        team_b_stats = next(s for s in standings if s["team"] == self.team_b)
        self.assertEqual(team_b_stats["sets_won"], 0)
        self.assertEqual(team_b_stats["sets_lost"], 2)
        self.assertEqual(team_b_stats["sets_balance"], -2)
        self.assertEqual(team_b_stats["points_scored"], 12)
        self.assertEqual(team_b_stats["points_conceded"], 22)
        self.assertEqual(team_b_stats["points_balance"], -10)

    def test_only_finished_matches_count(self):
        match = Match.objects.create(
            phase=Match.PHASE_GROUP,
            match_number=1000,
            bracket_type=Match.BRACKET_GROUP,
            group=self.group,
            team_a=self.team_a,
            team_b=self.team_b,
            status=Match.STATUS_READY,
            best_of=3,
            sort_order=0,
        )
        MatchSet.objects.create(
            match=match, set_number=1, team_a_points=11, team_b_points=5
        )

        standings = compute_group_standings(self.group)
        for s in standings:
            self.assertEqual(s["games"], 0)
            self.assertEqual(s["wins"], 0)

    def test_three_set_match_stats(self):
        self._create_finished_match(
            self.team_a, self.team_b, [(11, 5), (7, 11), (11, 9)]
        )

        standings = compute_group_standings(self.group)
        team_a_stats = next(s for s in standings if s["team"] == self.team_a)
        self.assertEqual(team_a_stats["games"], 1)
        self.assertEqual(team_a_stats["wins"], 1)
        self.assertEqual(team_a_stats["sets_won"], 2)
        self.assertEqual(team_a_stats["sets_lost"], 1)
        self.assertEqual(team_a_stats["sets_balance"], 1)
        self.assertEqual(team_a_stats["points_scored"], 29)
        self.assertEqual(team_a_stats["points_conceded"], 25)
        self.assertEqual(team_a_stats["points_balance"], 4)

    def test_five_team_group_round_robin(self):
        group = Group.objects.create(name="D")
        teams = []
        for i in range(5):
            teams.append(
                Team.objects.create(
                    player1_name=f"P{i*2+1}",
                    player2_name=f"P{i*2+2}",
                    group=group,
                )
            )

        counter = 2000
        for i, ta in enumerate(teams):
            for tb in teams[i + 1 :]:
                Match.objects.create(
                    phase=Match.PHASE_GROUP,
                    match_number=counter,
                    bracket_type=Match.BRACKET_GROUP,
                    group=group,
                    team_a=ta,
                    team_b=tb,
                    status=Match.STATUS_READY,
                    best_of=3,
                    sort_order=counter,
                )
                counter += 1

        self.assertEqual(
            Match.objects.filter(
                bracket_type=Match.BRACKET_GROUP, group=group
            ).count(),
            10,
        )
