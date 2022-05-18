from django.shortcuts import render
from .util import get_entry, list_entries
from markdown2 import markdown
from django import forms
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


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


def index(request):
    # url incoming: /wiki/
    print('INDEX 01')
    return show_list(request, entries_list=list_entries(), header="All Pages")


def search(request):
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


def display(request, title):
    print("DISPLAY 01")
    # user asks for a page by its title
    entry = get_entry(title)
    if entry:
        # asked page exists and its content is shown
        return show_entry(request, title, entry)
    else:
        # asked page does not exist
        return show_entry(request, title="Page not found", entry=" ")


class NewPageForm(forms.Form):
    newEntry = forms.CharField(label="New Entry")
    newEntryText = forms.CharField(label="New Entry Text", widget=forms.Textarea())


def newPage(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            newEntrySubtd = form.cleaned_data['newEntry']
            newEntryTextSubtd = form.cleaned_data['newEntryText']

            content = "# "+newEntrySubtd+"\n"+newEntryTextSubtd

            default_storage.save('./entries/'+newEntrySubtd+'.md', ContentFile(content))
            return render(request, "encyclopedia/display.html", {
                "entry": markdown(content), 'title': newEntrySubtd})

    return render(request, "encyclopedia/newpage.html", {"newPageForm": NewPageForm()})
