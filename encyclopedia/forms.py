from django import forms
from .util import list_entries


class EditPageForm(forms.Form):
    # form to edit entry's markdown content text
    newEntry = forms.CharField(label='Title')
    newEntryText = forms.CharField(widget=forms.Textarea(attrs={"style": "height:40vh"}))


class NewPageForm(EditPageForm):
    # form to add a new entry
    # in addition to edit form, the new entry should not exist already
    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('newEntry')
        # check if the new title already exists
        if title in list_entries():
            raise forms.ValidationError('Entry "'+title+'" already exists')
        return super().clean()
