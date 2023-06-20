import json
from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.utils import timezone

from ..forms import DiaryForm
from ..models import Diary, Keyword


@login_required(login_url="account:login")
def diary_create_before(request):
    if request.method == "POST":
        form = DiaryForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            # < -- 모델 처리 -- >

            content_list = request.POST.getlist("content[]")
            context = {
                "form": form,
                "content": "\n".join(content_list[1:]),
                "title": content_list[0],
                "keywords": ["즐거움", "행복", "산책"],  # 생성된 keyword
            }

            return render(request, "diary/diary_result_form.html", context)
    else:
        form = DiaryForm(request.user)
    context = {"form": form}
    return render(request, "diary/diary_form.html", context)


@login_required(login_url="account:login")
def diary_create(request):
    if request.method == "POST":
        form = DiaryForm(request.user, request.POST)
        if form.is_valid():
            diary = form.save(commit=False)
            diary.user = request.user
            diary.registered_time = timezone.now()
            diary.updated_time = timezone.now()
            diary.content = request.POST.get("content")
            diary.title = request.POST.get("title")

            checked_list_str = request.POST["keyword_list"]
            checked_list = json.loads(checked_list_str)
            keywords_list = []

            for keyword in checked_list:
                if keyword:
                    keyword_obj, created = Keyword.objects.get_or_create(word=keyword)
                    keywords_list.append(keyword_obj)

            diary.save()
            diary.keywords.set(keywords_list)

            return redirect("diary:index")
    else:
        form = DiaryForm(request.user)
    context = {"form": form}
    return render(request, "diary/diary_result_form.html", context)


@login_required(login_url="account:login")
def diary_bookmark(request, diary_id):
    diary = get_object_or_404(Diary, pk=diary_id)
    if request.user == diary.user:
        diary.bookmark = not diary.bookmark
        diary.save()
    query_params = {}
    page = request.POST.get("page")
    keyword = request.POST.get("keyword")
    pet_id = request.POST.get("pet_id")

    if page:
        query_params["page"] = page
    if keyword:
        query_params["keyword"] = keyword
    if pet_id:
        query_params["pet_id"] = pet_id

    query_string = urlencode(query_params)

    return HttpResponseRedirect(
        f"{resolve_url('diary:index')}?{query_string}#diary_{diary.id}"
    )
