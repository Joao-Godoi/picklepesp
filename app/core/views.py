from django.shortcuts import render
from django.views.decorators.cache import never_cache

from tournament.models import Match
from tournament.selectors import get_groups_page_data


@never_cache
def home(request):
    upcoming_matches = (
        Match.objects.filter(status__in=[Match.STATUS_READY, Match.STATUS_PENDING, Match.STATUS_BLOCKED])
        .select_related("team_a", "team_b")
        .order_by("sort_order", "match_number")[:6]
    )
    finished_count = Match.objects.filter(status=Match.STATUS_FINISHED).count()
    total_count = Match.objects.count()
    return render(
        request,
        "core/home.html",
        {
            "upcoming_matches": upcoming_matches,
            "finished_count": finished_count,
            "total_count": total_count,
        },
    )
