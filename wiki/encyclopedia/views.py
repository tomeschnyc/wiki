from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms
from . import util
import random
import markdown2

class SearchTitleForm(forms.Form):
    title = forms.CharField(label="Search")

class CreateNewForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'id' : 'new-title',
                'class': 'form-control'
                }))
    content = forms.CharField(
        label="Content: ",
        widget=forms.Textarea(
            attrs={
                'id': 'new-content',
                'class': 'form-control'
                }))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "title": "Encyclopedia",
        "form": SearchTitleForm()
    })

def display(request, title):
    if not util.match_title(title):
        return render(request, "encyclopedia/display.html", {
            "entry": str(f"{title} not found"),
            "title": "Encyclopedia",
            "form": SearchTitleForm()
        })

    return render(request, "encyclopedia/display.html", {
        "entry": markdown2.markdown(util.get_entry(title)),
        "title": title,
        "form": SearchTitleForm()
    })

def search(request):
    form = SearchTitleForm(request.GET)
    if form.is_valid():
        title = form.cleaned_data["title"]
        matched_entries = [entry for entry in util.list_entries() if title.lower() in entry.lower()]
        # If query string returns partial matches
        if not util.match_title(title) and matched_entries: 
            return render(request, "encyclopedia/index.html", {
                "entries": matched_entries,
                "title": "Encyclopedia",
                "form": SearchTitleForm()
            })
        else:
            return display(request, title)
    else: 
        return render(request, "encyclopedia/index.html", {
            "form": SearchTitleForm(),
            "entry": str(f"invalid input"),
            "title": "Encyclopedia"
        })

def new(request):
    new_entry = CreateNewForm()
    header = "Create New Page"
    return render(request, "encyclopedia/new.html", {
        "title": "Encyclopedia",
        "form": SearchTitleForm(),
        "new_entry": new_entry,
        "header": header
    })

def save(request):
    if request.method == "POST":
        form = CreateNewForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            if util.match_title(title):
                return render(request, "encyclopedia/error.html", {
                    "message": str(f"Error: Entry for {title} already exists. Please give another title."),
                    "form": SearchTitleForm()
                })
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse('display', args=[title]))
        else:
            return HttpResponse('invalid request')

def edit(request, title):
    content = util.get_entry(title)
    existing_entry = CreateNewForm(initial={
        'title': title,
        'content': content
    })
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "form": SearchTitleForm(),
        "entry": existing_entry, 
        "header": title
    })
    
def update(request):
    if request.method == "POST":
        form = CreateNewForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse('display', args=[title]))
        else:
            pass
    return HttpResponse('invalid request')

def random_page(request):
    page = random.choice(util.list_entries())
    return display(request, page)

