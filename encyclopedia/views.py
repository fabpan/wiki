from django.shortcuts import render
from .util import get_entry, list_entries
from markdown2 import markdown
from django import forms


def index(request):
        return render(request, "encyclopedia/index.html", {
        "entries": list_entries(), "header": "All Pages"
        })


def display(request, title=None):
    if request.method == "GET":
        entries = list_entries()
        q = request.GET.get("q")
        if q:
            if q.upper() in [entry.upper() for entry in entries]:
                title = q
            else:
                if q:
                    list_submatch = [s for s in entries if q.upper() in s.upper()]
                    case = len(list_submatch)
                    if case == 0:
                        header = "No results found for "+q
                    else:
                        header = q+" may refer to:"
                else:
                    header = "Pages available:"
                    list_submatch = entries

                return render(request, "encyclopedia/index.html", {
                    "entries": list_submatch, "header": header
                })


    entry = get_entry(title)
    if entry:
        return render(request, "encyclopedia/display.html", {
            "entry": markdown(entry), 'title': title})
    else:
        return render(request, "encyclopedia/display.html", {
            "entry": "<h1> '" + title + "' non trovato</h1>", 'title': title})


class NewPageForm(forms.Form):
    newEntry = forms.CharField(label="New Entry")
    newEntryText = forms.CharField(label="New Entry Text", widget=forms.Textarea())

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

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


