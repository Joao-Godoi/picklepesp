from django.contrib import admin

from tournament.models import Group, Team, Match, MatchSet

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
    fields = ["player1_name", "player2_name"]
    verbose_name = "Dupla"
    verbose_name_plural = "Duplas"


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    inlines = [TeamInline]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ["__str__", "group"]
    list_filter = ["group"]
    search_fields = ["player1_name", "player2_name"]
    list_select_related = ["group"]


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
                "fields": ("team_a", "team_b", "source_team_a", "source_team_b"),
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