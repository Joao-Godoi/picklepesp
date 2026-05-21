from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from tournament.models import Group, Team, Match, MatchSet
from tournament.services import determine_match_winner, validate_match_sets, propagate_match_result

admin.site.site_header = "PicklePesp - Administracao"
admin.site.site_title = "PicklePesp Admin"
admin.site.index_title = "Gerenciamento do Campeonato"


class MatchSetInline(admin.TabularInline):
    model = MatchSet
    extra = 0
    min_num = 0
    fields = ["set_number", "team_a_points", "team_b_points"]
    verbose_name = "Set"
    verbose_name_plural = "Sets"

    def get_max_num(self, request, obj=None):
        if obj and obj.best_of:
            return obj.best_of
        return 3


class TeamInline(admin.TabularInline):
    model = Team
    extra = 0
    fields = ["team_number", "player1_name", "player2_name"]
    verbose_name = "Dupla"
    verbose_name_plural = "Duplas"


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    inlines = [TeamInline]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ["team_number", "__str__", "player1_name", "player2_name", "group"]
    list_filter = ["group"]
    search_fields = ["player1_name", "player2_name", "team_number"]
    list_select_related = ["group"]
    ordering = ["team_number"]


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = [
        "match_number",
        "phase",
        "bracket_type",
        "team_a",
        "team_b",
        "winner",
        "status",
        "best_of",
    ]
    list_filter = ["phase", "bracket_type", "status", "group"]
    search_fields = [
        "team_a__player1_name",
        "team_a__player2_name",
        "team_b__player1_name",
        "team_b__player2_name",
        "source_team_a",
        "source_team_b",
    ]
    list_select_related = ["team_a", "team_b", "winner", "group"]
    inlines = [MatchSetInline]
    readonly_fields = ["winner"]
    fieldsets = (
        (
            "Identificacao",
            {
                "fields": (
                    "match_number",
                    "phase",
                    "bracket_type",
                    "group",
                    "status",
                    "best_of",
                    "sort_order",
                ),
            },
        ),
        (
            "Times",
            {
                "fields": (
                    "team_a",
                    "team_b",
                    "source_match_a",
                    "source_match_a_is_winner",
                    "source_match_b",
                    "source_match_b_is_winner",
                    "source_team_a",
                    "source_team_b",
                ),
            },
        ),
        (
            "Resultado",
            {
                "fields": ("winner", "final_position_winner", "final_position_loser"),
            },
        ),
        (
            "Planejamento",
            {
                "fields": ("scheduled_date",),
            },
        ),
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        obj = form.instance
        obj.refresh_from_db()

        if obj.status == Match.STATUS_FINISHED:
            errors = validate_match_sets(obj)
            if errors:
                for error in errors:
                    messages.error(request, error)
                obj.status = Match.STATUS_IN_PROGRESS
                Match.objects.filter(pk=obj.pk).update(
                    status=Match.STATUS_IN_PROGRESS
                )
                return

            winner = determine_match_winner(obj)
            if winner:
                Match.objects.filter(pk=obj.pk).update(winner=winner)
                obj.refresh_from_db()
                propagate_match_result(obj)
                messages.success(
                    request, f"Vencedor definido automaticamente: {winner}"
                )
            else:
                messages.warning(
                    request,
                    "Nao foi possivel determinar o vencedor a partir dos sets.",
                )
                obj.status = Match.STATUS_IN_PROGRESS
                Match.objects.filter(pk=obj.pk).update(
                    status=Match.STATUS_IN_PROGRESS
                )
        elif obj.team_a_id and obj.team_b_id and obj.status in (
            Match.STATUS_PENDING,
            Match.STATUS_BLOCKED,
        ):
            Match.objects.filter(pk=obj.pk).update(status=Match.STATUS_READY)
