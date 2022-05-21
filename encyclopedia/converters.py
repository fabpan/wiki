from .util import list_entries


class WikiEntryConverter:
    regex = '.+'  # any string

    def to_python(self, title):
        # accept only existing entries
        if title.upper() in [entry.upper() for entry in list_entries()]:
            return title
        else:
            raise ValueError

