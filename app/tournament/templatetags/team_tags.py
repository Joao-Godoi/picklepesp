from django import template

register = template.Library()


@register.filter
def team_display(team, is_admin=False):
    if not team:
        return ""
    if is_admin:
        return f"Dupla {team.team_number} - {team.player1_name} / {team.player2_name}"
    return f"Dupla {team.team_number}"
