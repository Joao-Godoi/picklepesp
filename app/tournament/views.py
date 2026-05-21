from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache

from tournament.selectors import (
    get_groups_page_data,
    get_playoffs_page_data,
    get_placements_page_data,
)


@never_cache
def groups(request):
    return redirect(reverse("home"))


@never_cache
def playoffs(request):
    return render(request, "tournament/playoffs.html", get_playoffs_page_data())


@never_cache
def placements(request):
    return render(
        request, "tournament/placements.html", get_placements_page_data()
    )