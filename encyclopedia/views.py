from django.shortcuts import render
from .util import get_entry, list_entries
from markdown2 import markdown
from django import forms
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect
from random import choice


def show_entry(request, title, entry=None):
    if not entry:
        entry = get_entry(title)
    return render(request, "encyclopedia/display.html", {
        "entry": markdown(entry), 'title': title})


def show_list(request, entries_list, header):
    print("SHOW LIST 01")
    return render(request, "encyclopedia/index.html", {
        "entries": entries_list, "header": header
    })


def index(request, title=None):
    # called when incoming url is ".../wiki/" or ".../wiki/title",
    # where title is a string different from "_newpage" and "_search"
    if not title:
        # incoming url is "/wiki/"
        print("w/o title")
        return show_list(request, entries_list=list_entries(), header="All Pages")
    else:
        # user asks for a page by its title
        print("w title", title)
        entry = get_entry(title)
        if entry:
            # asked page exists and its content is shown
            return show_entry(request, title, entry)
        else:
            # asked page does not exist
            return show_entry(request, title="Page not found", entry=" ")


def search(request):
    # called when incoming url is "../wiki/_search", usually followed by ..?q='value' (key named q end its string value)
    # user asks for a search
    q = request.GET.get("q")
    entries = list_entries()
    if q:
        # not empty target url incoming /_search/?q=... not empty
        if q.upper() in [entry.upper() for entry in entries]:
            # found full match entry , show page of the entry
            return show_entry(request, title=q)
        else:
            # look for partial matching entries/y
            entries_list = [s for s in entries if q.upper() in s.upper()]
            case = len(entries_list)
            if case == 0:
                # no partial matching found
                header = "No result found for " + q
            else:
                # found one or more partial matching
                header = q + " may refer to:"
            return show_list(request, entries_list, header)
    else:
        # empty search
        header = "Pages available:"
        entries_list = entries
        return show_list(request, entries_list, header)


class NewPageForm(forms.Form):
        newEntry = forms.CharField()
        newEntryText = forms.CharField(widget=forms.Textarea(attrs={"style":"height:40vh"}))


def update(request, title=None):
    if request.method == "POST":
        # replay of the user to the form
        form = NewPageForm(request.POST)
        if form.is_valid():
            newEntrySubtd = form.cleaned_data['newEntry']
            newEntryTextSubtd = form.cleaned_data['newEntryText']

            content = "# " + newEntrySubtd + "\n" + newEntryTextSubtd

            if 'savebtn' in request.POST:
                default_storage.save('./entries/' + newEntrySubtd + '.md', ContentFile(content))
                return show_entry(request, newEntrySubtd, content)
            elif 'previewbtn' in request.POST:
                PageForm = NewPageForm(initial={"newEntry": newEntrySubtd, "newEntryText": newEntryTextSubtd})
                PageForm['newEntry'].label = "Title"
                PageForm['newEntryText'].label = "Please, edit the page content here"
                return render(request, "encyclopedia/newpage.html",
                              {"newPageForm": PageForm,
                               "preview": markdown(content)})

    # send the form
    PageForm = NewPageForm()
    PageForm['newEntry'].label = "Title"
    if title:
        title = request.GET.get("title")
        entry = get_entry(title)
        content=entry.split('\n', 2)[-1]
        preview=markdown(entry)
        PageForm = NewPageForm(initial={"newEntry":title, "newEntryText": content})
        PageForm['newEntryText'].label = "Please, edit the page content here"
    else:
        PageForm['newEntryText'].label = "Please, enter the page content here"
        preview=""

    return render(request, "encyclopedia/newpage.html", {"newPageForm": PageForm, "preview": preview})


def newPage(request):
    return update(request)


def edit(request):
    # send the form
    title = request.GET.get("title")
    return update(request, title)

def random(request):

    return HttpResponseRedirect("/wiki/"+choice(list_entries()))