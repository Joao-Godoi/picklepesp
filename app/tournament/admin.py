from django.contrib import admin, messages
from django.utils.html import format_html

from tournament.models import Double, Group, Match, Set as MatchSet
from tournament.services import (
    ensure_sets,
    update_match_from_sets,
    propagate_match_result,
    recalculate_tournament,
)

admin.site.site_header = "PicklePesp - Administracao"
admin.site.site_title = "PicklePesp Admin"
admin.site.index_title = "Gerenciamento do Campeonato"


class SetInline(admin.TabularInline):
    model = MatchSet
    extra = 0
    min_num = 0
    fields = ["set_number", "points_double_1", "points_double_2", "winner"]
    readonly_fields = ["winner"]
    verbose_name = "Set"
    verbose_name_plural = "Sets"

    def get_max_num(self, request, obj=None):
        if obj and obj.best_of:
            return obj.best_of
        return 3


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ["name", "doubles_count"]
    search_fields = ["name"]
    fields = ["name", "doubles"]
    filter_horizontal = ["doubles"]

    def doubles_count(self, obj):
        return obj.doubles.count()
    doubles_count.short_description = "Duplas"


@admin.register(Double)
class DoubleAdmin(admin.ModelAdmin):
    list_display = ["name", "player_1", "player_2"]
    search_fields = ["name", "player_1", "player_2"]
    fields = ["name", "player_1", "player_2", "display_groups"]
    readonly_fields = ["display_groups"]

    def display_groups(self, obj):
        groups = obj.groups.all()
        if groups:
            return ", ".join(str(g) for g in groups)
        return "Nenhum grupo"
    display_groups.short_description = "Grupos"


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = [
        "match_number",
        "phase",
        "double_1",
        "double_2",
        "status",
        "winner",
        "dashboard_link",
    ]
    list_filter = ["phase", "status", "group"]
    search_fields = [
        "double_1__name",
        "double_1__player_1",
        "double_1__player_2",
        "double_2__name",
        "double_2__player_1",
        "double_2__player_2",
        "source_double_1_desc",
        "source_double_2_desc",
    ]
    list_select_related = ["double_1", "double_2", "winner", "group"]
    inlines = [SetInline]
    readonly_fields = ["status", "winner"]
    fieldsets = (
        (
            "Identificacao",
            {
                "fields": (
                    "match_number",
                    "phase",
                    "group",
                    "sort_order",
                ),
            },
        ),
        (
            "Duplas",
            {
                "fields": (
                    "double_1",
                    "double_2",
                    "source_match_1",
                    "source_match_1_is_winner",
                    "source_match_2",
                    "source_match_2_is_winner",
                    "source_double_1_desc",
                    "source_double_2_desc",
                ),
            },
        ),
        (
            "Resultado",
            {
                "fields": ("winner", "final_position_winner", "final_position_loser"),
            },
        ),
    )

    def dashboard_link(self, obj):
        from django.urls import reverse
        url = reverse("admin_match_edit", kwargs={"match_number": obj.match_number})
        return format_html('<a href="{}" target="_blank">Painel</a>', url)
    dashboard_link.short_description = "Painel"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.pk:
            ensure_sets(obj)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        obj = form.instance
        obj.refresh_from_db()

        update_match_from_sets(obj)
        obj.refresh_from_db()

        if obj.status == Match.STATUS_FINISHED:
            propagate_match_result(obj)
            messages.success(
                request,
                f"Partida finalizada automaticamente. Vencedor: {obj.winner}",
            )

        try:
            recalculate_tournament()
            messages.info(
                request,
                "Classificacao e confrontos recalculados automaticamente.",
            )
        except Exception as e:
            messages.error(request, f"Erro ao recalcular: {e}")
