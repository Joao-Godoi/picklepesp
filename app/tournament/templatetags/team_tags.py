from django import template

register = template.Library()


@register.filter
def team_display(double, is_admin=False):
    if not double:
        return ""
    if is_admin:
        return f"{double.name} - {double.player_1} / {double.player_2}"
    return double.name
