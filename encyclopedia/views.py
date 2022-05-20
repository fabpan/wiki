from django.shortcuts import render
from markdown2 import markdown
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect
from django.urls import reverse
from random import choice
from .forms import NewPageForm, EditPageForm
from .util import get_entry, list_entries, save_entry


def show_entry(request, title, entry=None):
    # common function to display wiki page
    if not entry:
        entry = get_entry(title)
    return render(request, "encyclopedia/display.html", {
        "entry": markdown(entry), 'title': title})


def show_list(request, entries_list, header):
    # common function to display lists of entries
    return render(request, "encyclopedia/index.html", {
        "entries": entries_list, "header": header
    })


def index(request, title=None):
    # called when incoming url is ".../wiki/" or ".../wiki/title",
    # where title is a string different from "_newpage" and "_search"
    if not title:
        # incoming url is "/wiki/"
        return show_list(request, entries_list=list_entries(), header="All Pages")
    else:
        # user asks for a page by its title
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
            return HttpResponseRedirect(reverse('index', args=[q]))
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


def edit(request):
    # called when incoming url is "/_edit", usually followed by ..?title='value' (key named "title" end its string value)
    if request.method == "POST":
        # form submitted by user
        form = EditPageForm(request.POST)
        if form.is_valid():
            EntrySubtd = form.cleaned_data['newEntry']
            EntryTextSubtd = form.cleaned_data['newEntryText']
            # compose content of the page
            content = "# " + EntrySubtd + "\n" + EntryTextSubtd
            # check which button has been submitted
            if 'savebtn' in request.POST:
                save_entry(EntrySubtd, content)
                return HttpResponseRedirect(reverse('index', args=[EntrySubtd]))
                # alternate solution return show_entry(request, newEntrySubtd, content)
            elif 'previewbtn' in request.POST:
                PageForm = EditPageForm(initial={"newEntry": EntrySubtd, "newEntryText": EntryTextSubtd})
                PageForm['newEntry'].label = "Title"
                PageForm['newEntryText'].label = "Please, edit the page content here or save it"
                return render(request, "encyclopedia/newpage.html",
                              {"PageForm": PageForm,
                                  "preview": markdown(content)})
    # send the form
    title = request.GET.get("title")
    entry = get_entry(title)
    content = entry.split('\n', 2)[-1]
    preview = markdown(entry)
    PageForm = EditPageForm(initial={"newEntry": title, "newEntryText": content})
    PageForm['newEntryText'].label = "Please, edit the page content here"

    return render(request, "encyclopedia/newpage.html", {"PageForm": PageForm, "preview": preview})


def newPage(request):
    # called when incoming url is "/_newpage"
    if request.method == "POST":
        # form submitted by user
        form = NewPageForm(request.POST)
        if form.is_valid():
            # extract submitted data
            EntrySubtd = form.cleaned_data['newEntry']
            EntryTextSubtd = form.cleaned_data['newEntryText']
            # compose content of the page
            content = "# " + EntrySubtd + "\n" + EntryTextSubtd
            # check which button has been submitted
            if 'savebtn' in request.POST:
                # store the page
                save_entry(EntrySubtd, content)
                return HttpResponseRedirect(reverse('index', args=[EntrySubtd]))

            else:   # 'previewbtn' in request.POST or others
                # set label (it seems the only one missed)
                form['newEntryText'].label = "Please, edit the page content here or save it"
                return render(request, "encyclopedia/newpage.html",
                              {"PageForm": form,
                               "preview": markdown(content)})
        else:
            # form submitted not valid, show the error message (included in the form) to the user
            return render(request, "encyclopedia/newpage.html",
                              {"PageForm": form,
                               "preview": ''})
    # build the form end return it to the user
    PageForm = NewPageForm()
    # PageForm['newEntry'].label = "Title"
    PageForm['newEntryText'].label = "Please, enter the page content here"
    preview = ""
    return render(request, "encyclopedia/newpage.html", {"PageForm": PageForm, "preview": preview})


def random(request):
    # called when incoming url is "/_random"
    return HttpResponseRedirect(reverse('index', args=[choice(list_entries())]))
