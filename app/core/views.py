from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache

from tournament.models import Match
from tournament.selectors import get_groups_page_data, get_overall_standings


@never_cache
def home(request):
    groups_data = get_groups_page_data()
    finished_count = Match.objects.filter(status=Match.STATUS_FINISHED).count()
    total_count = Match.objects.count()
    return render(
        request,
        "core/home.html",
        {
            "groups_data": groups_data,
            "finished_count": finished_count,
            "total_count": total_count,
        },
    )


@never_cache
def info(request):
    from tournament.selectors import get_info_page_data

    return render(request, "core/info.html", get_info_page_data())


@never_cache
def match_detail(request, match_number):
    from tournament.selectors import get_match_detail

    match = get_match_detail(match_number)
    if not match:
        from django.http import Http404
        raise Http404
    sets = list(match.sets.all().order_by("set_number"))
    is_admin = request.user.is_authenticated and request.user.is_staff
    return render(request, "core/match_detail.html", {"match_obj": match, "sets": sets, "is_admin": is_admin})


@never_cache
def rankings(request):
    standings = get_overall_standings()
    return render(request, "core/rankings.html", {"standings": standings})


@never_cache
def admin_dashboard(request):
    if not (request.user.is_authenticated and request.user.is_staff):
        return redirect(f"{reverse('admin:login')}?next={request.path}")
    from tournament.selectors import get_admin_matches

    data = get_admin_matches()
    return render(request, "core/admin_dashboard.html", data)


@never_cache
def admin_match_edit(request, match_number):
    if not (request.user.is_authenticated and request.user.is_staff):
        return redirect(f"{reverse('admin:login')}?next={request.path}")

    match = get_object_or_404(Match, match_number=match_number)
    from tournament.services import ensure_sets, update_match_from_sets, propagate_match_result

    if request.method == "POST":
        for s in match.sets.all().order_by("set_number"):
            p1 = request.POST.get(f"set_{s.set_number}_p1")
            p2 = request.POST.get(f"set_{s.set_number}_p2")
            if p1 is not None and p2 is not None:
                try:
                    s.points_double_1 = int(p1)
                    s.points_double_2 = int(p2)
                    s.save()
                except (ValueError, TypeError):
                    pass

        update_match_from_sets(match)
        match.refresh_from_db()

        if match.status == Match.STATUS_FINISHED:
            from tournament.services import recalculate_tournament
            propagate_match_result(match)
            recalculate_tournament()

        from django.contrib import messages
        messages.success(request, f"Partida J{match.match_number} atualizada com sucesso.")
        return redirect("admin_match_edit", match_number=match_number)

    ensure_sets(match)
    match.refresh_from_db()
    sets = list(match.sets.all().order_by("set_number"))

    from tournament.selectors import get_admin_matches
    data = get_admin_matches()
    data["edit_match"] = match
    data["sets"] = sets
    return render(request, "core/admin_match_edit.html", data)