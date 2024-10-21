import panel as pn
import param

from tseda.datastore import IndividualsTable

from .core import View
from .map import GeoMap


class IndividualsPage(View):
    key = "individuals"
    title = "Individuals"
    geomap = param.ClassSelector(class_=GeoMap)
    data = param.ClassSelector(class_=IndividualsTable)

    def __init__(self, **params):
        super().__init__(**params)
        self.geomap = GeoMap(datastore=self.datastore)
        self.data = self.datastore.individuals_table

    def __panel__(self):
        return pn.Column(self.geomap, self.data)

    def sidebar(self):
        return pn.Column(
            self.geomap.sidebar,
            pn.pane.Markdown("## Individuals table options"),
            self.data.param.page_size,
            self.data.param.toggle,
            self.data.param.population_from,
            self.data.param.sample_set_to,
        )
