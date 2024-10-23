import panel as pn
import param

from tseda.datastore import SampleSetsTable

from .core import View


class SampleSetsPage(View):
    key = "sample_sets"
    title = "Sample Sets"
    data = param.ClassSelector(class_=SampleSetsTable)

    def __init__(self, **params):
        super().__init__(**params)
        self.data = self.datastore.sample_sets_table

    def __panel__(self):
        return pn.Column(self.data)

    def sidebar(self):
        return pn.Column(self.data.sidebar)
