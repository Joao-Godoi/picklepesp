from django.shortcuts import render


def groups(request):
    return render(request, "tournament/groups.html")


def playoffs(request):
    return render(request, "tournament/playoffs.html")


def placements(request):
    return render(request, "tournament/placements.html")
