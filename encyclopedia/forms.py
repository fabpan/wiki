from django import forms
from .util import list_entries


class EditPageForm(forms.Form):
    newEntry = forms.CharField(label='Title')
    newEntryText = forms.CharField(widget=forms.Textarea(attrs={"style": "height:40vh"}))


class NewPageForm(EditPageForm):
    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('newEntry')
        if title in list_entries():
            raise forms.ValidationError('Entry "'+title+'" already exists')
        return super().clean()
