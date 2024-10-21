import panel as pn
import param
from panel.viewable import Viewer

from tseda.datastore import DataStore


class View(Viewer):
    key = param.String()
    title = param.String()
    datastore = param.ClassSelector(class_=DataStore)

    def __init__(self, **params):
        super().__init__(**params)
        print(id(self.datastore))

    def sidebar(self):
        return pn.Column(pn.pane.Markdown(f"# {self.title}"))
