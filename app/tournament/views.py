from django.shortcuts import render

from tournament.selectors import get_groups_page_data, get_playoffs_page_data, get_placements_page_data


def groups(request):
    return render(request, "tournament/groups.html", {"groups_data": get_groups_page_data()})


def playoffs(request):
    return render(request, "tournament/playoffs.html", get_playoffs_page_data())


def placements(request):
    return render(request, "tournament/placements.html", get_placements_page_data())
