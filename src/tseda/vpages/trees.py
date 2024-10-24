"""Module to plot local trees

TODO:

- fix bounds of position / treeid parameters
"""

import ast

import holoviews as hv
import numpy as np
import panel as pn
import param

from tseda import config

from .core import View

hv.extension("bokeh")


def eval_options(options):
    """Evaluate options parameter."""
    return ast.literal_eval(options)


class Tree(View):
    tree_index = param.Integer(
        default=0, bounds=(0, None), doc="Get tree by zero-based index"
    )
    position = param.Integer(
        default=None, bounds=(1, None), doc="Get tree at genome position (bp)"
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
    next = param.Action(
        lambda x: x.next_tree(), doc="Next tree", label="Next tree"
    )
    prev = param.Action(
        lambda x: x.prev_tree(), doc="Previous tree", label="Previous tree"
    )

    symbol_size = param.Number(default=5, bounds=(0, None), doc="Symbol size")

    def next_tree(self):
        self.position = None
        self.tree_index += 1  # pyright: ignore[reportOperatorIssue]

    def prev_tree(self):
        self.position = None
        self.tree_index = max(0, self.tree_index - 1)  # pyright: ignore[reportOperatorIssue]

    @property
    def default_css(self):
        """Default css styles for tree nodes"""
        styles = []
        for (
            ssid,
            ss,
        ) in self.datastore.sample_sets_table.data.rx.value.iterrows():
            s = f".node.p{ssid} > .sym " + "{" + f"fill: {ss.color} " + "}"
            styles.append(s)
        css_string = " ".join(styles)
        return css_string

    @param.depends(
        "width", "height", "position", "options", "symbol_size", "tree_index"
    )
    def __panel__(self):
        options = eval_options(self.options)
        if self.position is not None:
            tree = self.datastore.tsm.ts.at(self.position)
            self.tree_index = tree.index
            position = self.position
        else:
            tree = self.datastore.tsm.ts.at_index(self.tree_index)
            position = int(np.mean(tree.get_interval()))
        return pn.Column(
            pn.pane.Markdown(
                f"## Tree index {self.tree_index} (position {position})"
            ),
            pn.pane.HTML(
                tree.draw_svg(
                    size=(self.width, self.height),
                    symbol_size=self.symbol_size,
                    style=self.default_css,
                    **options,
                ),
            ),
            pn.Row(
                self.param.prev,
                self.param.next,
            ),
        )

    def sidebar(self):
        return pn.Column(
            pn.Card(
                self.param.position,
                self.param.tree_index,
                self.param.width,
                self.param.height,
                self.param.options,
                self.param.symbol_size,
                collapsed=True,
                title="Tree plotting options",
                header_background=config.SIDEBAR_BACKGROUND,
                active_header_background=config.SIDEBAR_BACKGROUND,
                styles=config.VCARD_STYLE,
            ),
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
