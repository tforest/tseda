import panel as pn

from .core import View


class OverviewPage(View):
    key = "overview"
    title = "Overview"

    def __panel__(self):
        return pn.Column(pn.pane.HTML(self.datastore.tsm.ts))

    # def sidebar(self):
    #     return pn.Column(pn.pane.Markdown("# Overview"))
