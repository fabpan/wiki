from django.shortcuts import render
from markdown2 import markdown
from django.http import HttpResponseRedirect
from django.urls import reverse
from random import choice
from .forms import NewPageForm, EditPageForm
from .util import get_entry, list_entries, save_entry


def show_list(request, entries_list, header):
    # common function/view to display lists of entries
    return render(request, "encyclopedia/index.html", {
        "entries": entries_list, "header": header
    })


def index(request, title=None):
    # called when incoming url is ".../wiki/" or ".../wiki/title",
    # where title is a string different from "_newpage", "_random", "_edit" and "_search"
    if not title:
        # incoming url is "/wiki/"
        return show_list(request, entries_list=list_entries(), header="All Pages")
    else:
        # user asks for a page by its title
        entry = get_entry(title)
        if entry:
            # asked page exists and its content is shown
            return render(request, "encyclopedia/display.html", {
                "entry": markdown(entry), 'title': title})
        else:
            # asked page does not exist
            # urls dispatcher should have intercepted this request,  this branch is kept as a further precaution
            return handler404(request, title)


def search(request):
    # called when incoming url is "../wiki/_search", usually followed by ..?q='value' (key named q end its string value)
    # user asks for a search
    # extract the title of the entry requested
    q = request.GET.get("q")
    # call the function that provide the complete list of the entries
    entries = list_entries()
    if q:
        # not empty target url incoming /_search/?q=... not empty
        if q.lower() in [entry.lower() for entry in entries]:
            # found full matching entry (case insesitive), show page of the entry
            return HttpResponseRedirect(reverse('handler404', args=[q]))
        else:
            # no full matching entry
            # look for partial matching entries and update entries_list
            entries_list = [s for s in entries if q.lower() in s.lower()]
            case = len(entries_list)
            if case == 0:
                # no partial matching found
                header = f"No result found for {q}"
            else:
                # found one or more partial matching
                header = f"'{q}' may refer to:"
            return show_list(request, entries_list, header)
    else:
        # empty target for search
        # shows all pages
        header = "Pages available:"
        entries_list = entries
        return show_list(request, entries_list, header)


def updatePage(request, action):
    # called when incoming url is "/_newpage" (action='newpage') or "/-edit (action = edit)
    # since codes for the two actions have a large common part, I implemented them in the same view
    if request.method == "POST":
        # form submitted by user
        if action == "edit":
            form = EditPageForm(request.POST)
        else:
            form = NewPageForm(request.POST)
        if form.is_valid():
            # extract submitted data
            EntrySubtd = form.cleaned_data['newEntry']
            EntryTextSubtd = form.cleaned_data['newEntryText']
            # compose content of the page
            content = "# " + EntrySubtd + "\n\n" + EntryTextSubtd
            # check which button has been submitted
            if 'savebtn' in request.POST:
                # store the page
                save_entry(EntrySubtd, content)
                return HttpResponseRedirect(reverse('handler404', args=[EntrySubtd]))

            else:   # 'previewbtn' in request.POST (or others)
                # set label
                form['newEntryText'].label = "Please, edit the page contents here or save it"
                return render(request, "encyclopedia/newpage.html",
                              {"PageForm": form,
                               "preview": markdown(content)})
        else:
            # form submitted not valid, show the error message (included in form) to the user
            # when form is newPageForm, validation in forms.py include check if the entry already exists
            return render(request, "encyclopedia/newpage.html",
                          {"PageForm": form, "preview": ''})
    # build the form end return it to the user
    if action == "edit":
        # extract the title of the page to be edited
        title = request.GET.get("title")
        entry = get_entry(title)
        # split title and content of the entry
        content = entry.split('\n', 2)[-1]
        # convert markdown to HTML
        preview = markdown(entry)
        # form is filled with the content to be edited
        PageForm = EditPageForm(initial={"newEntry": title, "newEntryText": content})
        PageForm['newEntryText'].label = "Please, edit the page contents here"
    else:
        # create a form with empty input cells
        PageForm = NewPageForm()
        PageForm['newEntryText'].label = "Please, enter the page contents here"
        preview = ""
    return render(request, "encyclopedia/newpage.html", {"PageForm": PageForm, "preview": preview})


def random(request):
    # called when incoming url is "/_random"
    return HttpResponseRedirect(reverse('handler404', args=[choice(list_entries())]))


def handler404(request, title):
    # called when incoming url cannot be dispatched to others views
    return render(request, "encyclopedia/404.html", {"title": title}, status=404)

