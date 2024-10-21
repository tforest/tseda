import ast

import holoviews as hv
import panel as pn
import param

from tseda import config

from .core import View

hv.extension("bokeh")


def eval_options(options):
    """Evaluate options parameter."""
    return ast.literal_eval(options)


class Tree(View):
    # treeid = param.Integer(default=0, bounds=(0, None), doc="Get
    # tree by zero-based index")
    position = param.Integer(
        default=1, bounds=(1, None), doc="Get tree at genome position (bp)"
    )
    width = param.Integer(default=800, doc="Width of the tree plot")
    height = param.Integer(default=800, doc="Height of the tree plot")
    options = param.String(
        default="{'y_axis': 'time', 'node_labels': {}}",
        doc=(
            "Additional options for configuring tree plot. "
            "Must be a valid dictionary string."
        ),
    )

    @property
    def default_css(self):
        """Default css styles for tree nodes"""
        styles = []
        for (
            ssid,
            ss,
        ) in self.datastore.sample_sets_table.data.rx.value.iterrows():
            s = f".node.p{ssid} > .sym " + "{" + f"fill: {ss.color}" + "}"
            styles.append(s)
        css_string = " ".join(styles)
        return css_string

    @param.depends("width", "height", "position", "options")
    def __panel__(self):
        options = eval_options(self.options)
        return pn.pane.HTML(
            self.datastore.tsm.ts.at(self.position).draw_svg(
                size=(self.width, self.height),
                style=self.default_css,
                **options,
            )
        )

    def sidebar(self):
        return pn.Card(
            self.param.position,
            self.param.width,
            self.param.height,
            self.param.options,
            collapsed=True,
            title="Tree plotting options",
            header_background=config.SIDEBAR_BACKGROUND,
            active_header_background=config.SIDEBAR_BACKGROUND,
            styles=config.VCARD_STYLE,
        )


class TreesPage(View):
    key = "trees"
    title = "Trees"
    data = param.ClassSelector(class_=Tree)

    def __init__(self, **params):
        super().__init__(**params)
        self.data = Tree(datastore=self.datastore)

    def __panel__(self):
        return pn.Column(
            self.data,
        )

    def sidebar(self):
        return pn.Column(
            self.data.sidebar,
        )
