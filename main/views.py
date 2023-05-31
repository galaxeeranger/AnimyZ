from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, HttpResponse, JsonResponse
from main.db import update_views, update_watch
from main.html_gen import (
    animeRecHtml,
    animeRecHtml2,
    episodeHtml,
    get_eps_html,
    get_eps_html2,
    get_recent_html,
    get_search_html,
    get_selector_btns,
    get_genre_html,
    get_trending_html,
    slider_gen,
)
from main.anilist import Anilist
from main.others import get_atitle, get_other_title, get_studios, get_t_from_u
from main.techzapi import TechZApi
from django.conf import settings

TechZApi = TechZApi(settings.API_KEY)

# def favicon(request):
#     return redirect('https://cdn.jsdelivr.net/gh/TechShreyash/AnimeDex@main/static/img/favicon.ico')

def home(request):
    context = {}
    context['div1'] = get_trending_html(TechZApi.top_animedex())
    context['div2'] = get_recent_html(TechZApi.gogo_latest())
    context['sliders'] = slider_gen()

    update_views("home-animedex")

    return render(request, 'index.html', context)

def get_anime(request, anime):
    try:
        data = TechZApi.gogo_anime(anime)
        TITLE = data.get("title")
        IMG = data.get("img")
        LANG = data.get("lang")
        TYPE = data.get("type")
        WATCHNOW = "/episode/" + data.get("id") + "/1"
        OTHER = data.get("other name")
        TOTAL = str(data.get("total_ep"))
        YEAR = data.get("year")
        STATUS = data.get("status")
        STUDIO = data.get("studios")
        GENERES = get_genre_html(data.get("genre").split(","))
        SYNOPSIS = data.get("summary")
        x = anime.lower()
        if x.endswith("-dub"):
            x = x[:-4]
        if x.endswith("-sub"):
            x = x[:-4]
        x = get_t_from_u(x).replace("-", " ")

        try:
            DISPLAY_ANIME = animeRecHtml(Anilist().get_recommendation(x))
        except:
            DISPLAY_ANIME = ""
        EPISODES = get_eps_html(data=data.get("episodes"))

        context = {
            "IMG": IMG,
            "TITLE": TITLE,
            "LANG": LANG,
            "TYPE": TYPE,
            "WATCHNOW": WATCHNOW,
            "OTHER": OTHER,
            "TOTAL": TOTAL,
            "YEAR": YEAR,
            "STATUS": STATUS,
            "STUDIO": STUDIO,
            "EPISODE":EPISODES,
            "GENERES":GENERES,
            "SYNOPSIS":SYNOPSIS,
            "DISPLAY_ANIME":DISPLAY_ANIME,
        }
        html = render(request, "anime.html", context)
    except:
        anime = anime.lower()
        if anime.endswith("-dub"):
            anime = anime[:-4]
        if anime.endswith("-sub"):
            anime = anime[:-4]
        anime = get_t_from_u(anime).replace("-", " ")
        data = Anilist().anime(anime)

        IMG = data.get("coverImage").get("medium").replace("small", "medium")
        if not IMG:
            IMG = data.get("bannerImage")
        TITLE = get_atitle(data.get("title"))
        SYNOPSIS = data.get("description")
        OTHER = get_other_title(data.get("title"))
        STUDIO = get_studios(data.get("studios").get("nodes"))
        TOTAL = str(data.get("episodes"))
        GENERES = get_genre_html(data.get("genres"))
        DISPLAY_ANIME = animeRecHtml2(data.get("recommendations").get("edges"))

        try:
            EPISODES = get_eps_html(api=TechZApi, anime=TITLE)
            id = get_eps_html(api=TechZApi, anime=TITLE)
        except:
            EPISODES = ""
            id = "#"

        SEASON = str(data.get("season")) + " " + str(data.get("seasonYear"))
        YEAR = data.get("seasonYear")
        TYPE = data.get("format")
        STATUS = data.get("status")
        WATCHNOW = "/episode/" + id + "/1"

        context = {
            "IMG": IMG,
            "TITLE": TITLE,
            "LANG": LANG,
            "TYPE": TYPE,
            "WATCHNOW": WATCHNOW,
            "OTHER": OTHER,
            "TOTAL": TOTAL,
            "YEAR": YEAR,
            "STATUS": STATUS,
            "STUDIO": STUDIO,
            "EPISODE":EPISODES,
            "GENERES":GENERES,
            "SYNOPSIS":SYNOPSIS,
            "DISPLAY_ANIME":DISPLAY_ANIME,
        }
        html = render(request, "anime.html", context)

    # html = html.replace("GENERES", GENERES)
    # html = html.replace("EPISODES", EPISODES)
    # html = html.replace("DISPLAY_ANIME", DISPLAY_ANIME)
    # html = html.replace("SYNOPSIS", SYNOPSIS)
    update_views(anime)
    return html

def get_episode(request, anime, episode):
    anime = get_t_from_u(anime).lower()
    episode = int(episode)

    try:
        data = TechZApi.gogo_episode(f"{anime}-episode-{episode}")
        x = TechZApi.gogo_anime(anime)
        total_eps = x.get("total_ep")
        ep_list = x.get("episodes")
    except:
        search = TechZApi.gogo_search(anime)[0]
        anime = search.get("id")
        total_eps = search.get("total_ep")
        ep_list = search.get("episodes")
        data = TechZApi.gogo_episode(f"{anime}-episode-{episode}")
    ep_list = get_eps_html2(ep_list)
    btn_html = get_selector_btns(f"/episode/{anime}/", int(episode), int(total_eps))
    ep_html = episodeHtml(data, f"{anime} - Episode {episode}")
    # iframe = episodeHtml(data, f"{anime} - Episode {episode}")
    iframe = episodeHtml(data, f"{anime} - Episode {episode}")

    # print(iframe,"ffffffffff")

    context = {
        "title": f"{anime} - Episode {episode}",
        "heading": anime,
        "iframe": iframe,
        "PROSLO": btn_html,
        "SERVER": ep_html,
        "EPISOS": ep_list,
    }

    update_watch(anime)
    return render(request, "episode.html", context=context)


def search_anime(request):
    if request.method == "GET":
        anime = request.GET.get("query").lower().strip()

        if anime.endswith("-dub"):
            anime = anime[:-4]
        if anime.endswith("-sub"):
            anime = anime[:-4]

        context = {
            "aid": anime.replace("+", " "),
        }
        html = render(request, "search.html", context=context)

        data = TechZApi.gogo_search(anime)
        display = get_search_html(data)

        html = html.content.decode("utf-8").replace("SEARCHED", display)
        update_views("search-animedex")
        return HttpResponse(html)


def get_embed(request):
    try:
        url = request.GET.get("url")
        file = False
        if url:
            if ".mp4" in url or ".mkv" in url:
                file = url
            else:
                if request.GET.get("token"):
                    url += f'&token={request.GET.get("token")}'
                if request.GET.get("expires"):
                    url += f'&expires={request.GET.get("expires")}'

                file = TechZApi.gogo_stream(url)
                server = int(request.GET.get("server"))
                if server == 1:
                    file = file.get("source")[0].get("file")
                elif server == 2:
                    file = file.get("source_bk")[0].get("file")
        else:
            file = request.GET.get("file")
    except Exception as e:
        print(e)
        file = request.GET.get("file")
    if not file:
        return redirect(url)
    title = request.GET.get("title")

    return render(request, "vid.html", {"m3u8": file, "title": title})

def latest_view(request, page):
    try:
        data = TechZApi.gogo_latest(page)
        html = get_recent_html(data)
        return JsonResponse({'html': html})
    except:
        return JsonResponse({'html': ''})