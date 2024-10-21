import panel as pn

from .core import View

pn.extension("tabulator")


class SampleSetsPage(View):
    key = "sample_sets"
    title = "Sample Sets"

    def __panel__(self):
        data = self.datastore.sample_sets_table.data
        table = pn.widgets.Tabulator(
            data,
            layout="fit_columns",
            selectable=True,
            page_size=100,
            pagination="remote",
            margin=10,
        )
        return table

    # def sidebar(self):
    #     return pn.Column(pn.pane.Markdown("# Sample Sets"))
