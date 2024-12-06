"""Module to plot local trees

TODO:

- fix bounds of position / treeid parameters
"""

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
    search_by = pn.widgets.ToggleGroup(
        name="Search By",
        options=["Position", "Tree Index"],
        behavior="radio",
        button_type="primary",
    )

    tree_index = param.Integer(
        default=0,
        doc="""Get tree by zero-based index. If multiple trees are 
        shown, this is the index of the first tree.""",
    )
    position = param.Integer(
        default=None,
        doc="""Get tree at genome position (bp). If multiple trees are 
        shown, this is the position of the first tree.""",
    )

    position_index_warning = pn.pane.Alert(
        "The input for position or tree index is out of bounds for the specified number of trees.",
        alert_type="warning",
        visible=False,
    )

    width = param.Integer(default=750, doc="Width of the tree plot")
    height = param.Integer(default=520, doc="Height of the tree plot")
    next = param.Action(
        lambda x: x.next_tree(), doc="Next tree", label="Next tree"
    )
    prev = param.Action(
        lambda x: x.prev_tree(), doc="Previous tree", label="Previous tree"
    )

    num_trees = pn.widgets.Select(
        name="Number of trees",
        options=[1, 2, 3, 4, 5, 6],
        value=1,
        description="""Select the number of trees to display. The first tree 
        will represent your selected chromosome position or tree index.""",
    )

    y_axis = pn.widgets.Checkbox(name="Include y-axis", value=True)
    y_ticks = pn.widgets.Checkbox(name="Include y-ticks", value=True)
    x_axis = pn.widgets.Checkbox(name="Include x-axis", value=False)
    sites_mutations = pn.widgets.Checkbox(
        name="Include sites and mutations", value=True
    )
    pack_unselected = pn.widgets.Checkbox(
        name="Pack unselected sample sets", value=False, width=197
    )
    options_doc = pn.widgets.TooltipIcon(
        value=(
            """Select various elements to include in your graph.
            Pack unselected sample sets: Selecting this option 
            will allow large polytomies involving unselected 
            samples to be summarised as a dotted line. Selection 
            of samples and sample sets can be done on the 
            Individuals page."""
        ),
    )

    node_labels = param.String(
        default="{}",
        doc=(
            """Show custom labels for the nodes (specified by ID).
            Any nodes not present will not have a label.
            Examle: {1: 'label1', 2: 'label2',...}"""
        ),
    )
    additional_options = param.String(
        default="{}",
        doc=(
            """Add more options as specified by the documentation.
            Must be a valid dictionary.
            Examle: {'title': 'My Tree',...}"""
        ),
    )

    symbol_size = param.Number(default=8, bounds=(0, None), doc="Symbol size")

    advanced_warning = pn.pane.Alert(
        "The inputs for the advanced options are not valid.",
        alert_type="warning",
        visible=False,
    )

    slider = pn.widgets.IntSlider(name="Chromosome Position")

    def __init__(self, **params):
        super().__init__(**params)
        self.slider.end = int(self.datastore.tsm.ts.sequence_length - 1)

    def next_tree(self):
        self.position = None
        self.tree_index = min(
            self.datastore.tsm.ts.num_trees - self.num_trees.value,
            int(self.tree_index) + 1,
        )
        # pyright: ignore[reportOperatorIssue]

    def prev_tree(self):
        self.position = None
        self.tree_index = max(0, int(self.tree_index) - 1)
        # pyright: ignore[reportOperatorIssue]

    @property
    def default_css(self):
        """Default css styles for tree nodes"""
        styles = []
        sample_sets = self.datastore.sample_sets_table.data.rx.value
        individuals = self.datastore.individuals_table.data.rx.value
        sample2ind = self.datastore.individuals_table.sample2ind
        for n in self.datastore.individuals_table.samples():
            ssid = individuals.loc[sample2ind[n]].sample_set_id
            ss = sample_sets.loc[ssid]
            s = f".node.n{n} > .sym " + "{" + f"fill: {ss.color} " + "}"
            styles.append(s)
        css_string = " ".join(styles)
        return css_string

    def check_inputs(self):
        if self.position is not None:
            if (
                int(self.position) < 0
                or int(self.position) >= self.datastore.tsm.ts.sequence_length
            ):
                raise ValueError
            elif int(
                self.datastore.tsm.ts.at(self.position).index
                + self.num_trees.value
            ) > int(self.datastore.tsm.ts.num_trees):
                raise ValueError
        if self.tree_index is not None and (
            int(self.tree_index) < 0
            or int(self.tree_index) + int(self.num_trees.value)
            > self.datastore.tsm.ts.num_trees
        ):
            raise ValueError
        else:
            self.position_index_warning.visible = False

    def handle_advanced(self):
        if self.sites_mutations.value is True:
            omit_sites = not self.sites_mutations.value
        else:
            omit_sites = True
        if self.y_ticks.value is True:
            y_ticks = None
        else:
            y_ticks = {}
        if self.node_labels == "":
            self.node_labels = "{}"
        if self.additional_options == "":
            self.additional_options = "{}"
        return omit_sites, y_ticks

    @param.depends("position", watch=True)
    def update_slider(self):
        if self.position is not None:
            self.slider.value = self.position

    @param.depends("slider.value_throttled", watch=True)
    def update_position(self):
        self.position = self.slider.value

    def plot_tree(
        self, tree, omit_sites, y_ticks, node_labels, additional_options
    ):
        try:
            plot = tree.draw_svg(
                size=(self.width, self.height),
                symbol_size=self.symbol_size,
                y_axis=self.y_axis.value,
                x_axis=self.x_axis.value,
                omit_sites=omit_sites,
                node_labels=node_labels,
                y_ticks=y_ticks,
                pack_untracked_polytomies=self.pack_unselected.value,
                style=self.default_css,
                **additional_options,
            )
            self.advanced_warning.visible = False
        except (ValueError, SyntaxError, TypeError):
            plot = tree.draw_svg(
                size=(self.width, self.height),
                y_axis=True,
                node_labels={},
                style=self.default_css,
            )
            self.advanced_warning.visible = True
        pos1 = int(tree.get_interval()[0])
        pos2 = int(tree.get_interval()[1]) - 1
        return pn.Column(
            pn.pane.HTML(
                f"<h2>Tree index {tree.index}"
                f" (position {pos1} - {pos2})</h2>",
                sizing_mode="stretch_width",
            ),
            pn.pane.HTML(plot),
        )

    def get_all_trees(self, trees):
        if not trees:
            return None
        rows = [pn.Row(*trees[i : i + 2]) for i in range(0, len(trees), 2)]
        return pn.Column(*rows)

    @param.depends("num_trees.value", watch=True)
    def multiple_trees(self):
        if int(self.num_trees.value) > 1:
            self.width = 470
            self.height = 470
            self.y_axis.value = False
            self.x_axis.value = False
            self.y_ticks.value = False
            self.sites_mutations.value = False
            self.pack_unselected.value = True
            self.symbol_size = 6
        else:
            self.width = 750
            self.height = 520
            self.y_axis.value = True
            self.x_axis.value = False
            self.y_ticks.value = True
            self.sites_mutations.value = True
            self.pack_unselected.value = False
            self.symbol_size = 8

    @param.depends(
        "width",
        "height",
        "position",
        "symbol_size",
        "tree_index",
        "num_trees.value",
        "y_axis.value",
        "y_ticks.value",
        "x_axis.value",
        "sites_mutations.value",
        "pack_unselected.value",
        "node_labels",
        "additional_options",
        "slider.value_throttled",
    )
    def __panel__(self):
        try:
            self.check_inputs()
        except ValueError:
            self.position_index_warning.visible = True
            raise ValueError("Inputs for position or tree index are not valid")

        sample_sets = self.datastore.individuals_table.sample_sets()
        selected_samples = [
            int(i) for sublist in list(sample_sets.values()) for i in sublist
        ]
        if len(selected_samples) < 1:
            self.pack_unselected.value = False
            self.pack_unselected.disabled = True
        else:
            self.pack_unselected.disabled = False
        omit_sites, y_ticks = self.handle_advanced()
        try:
            node_labels = eval_options(self.node_labels)
            additional_options = eval_options(self.additional_options)
        except (ValueError, SyntaxError, TypeError):
            node_labels = None
            additional_options = None
            self.advanced_warning.visible = True
        trees = []
        for i in range(self.num_trees.value):
            if self.position is not None:
                tree = self.datastore.tsm.ts.at(self.position)
                self.tree_index = tree.index
                tree = self.datastore.tsm.ts.at_index(
                    (tree.index + i), tracked_samples=selected_samples
                )
            else:
                tree = self.datastore.tsm.ts.at_index(
                    int(self.tree_index) + i, tracked_samples=selected_samples
                )
                self.slider.value = int(tree.get_interval()[0])
            trees.append(
                self.plot_tree(
                    tree, omit_sites, y_ticks, node_labels, additional_options
                )
            )
        all_trees = self.get_all_trees(trees)
        return pn.Column(
            all_trees,
            pn.pane.Markdown("**Tree plot** - Lorem Ipsum"),
            self.slider,
            pn.Row(
                self.param.prev,
                self.param.next,
            ),
        )

    def update_sidebar(self):
        """Dynamically update the sidebar based on searchBy value."""
        if self.search_by.value == "Tree Index":
            self.position = None
            fields = [self.param.tree_index]
        else:
            fields = [self.param.position]

        sidebar_content = pn.Column(
            pn.Card(
                self.search_by,
                *fields,
                self.param.width,
                self.param.height,
                collapsed=False,
                title="Tree plotting options",
                header_background=config.SIDEBAR_BACKGROUND,
                active_header_background=config.SIDEBAR_BACKGROUND,
                styles=config.VCARD_STYLE,
            ),
            self.position_index_warning,
        )
        return sidebar_content

    @param.depends("search_by.value", watch=True)
    def sidebar(self):
        return self.update_sidebar()

    def advanced_options(self):
        doc_link = """https://tskit.dev/tskit/docs/stable/python-api.html#tskit.TreeSequence.draw_svg"""
        sidebar_content = pn.Column(
            pn.Card(
                pn.pane.HTML(
                    f"""<b>See the <a 
                    href={doc_link}>
                    tskit documentation</a> for more information
                    about these plotting options.<b>"""
                ),
                self.num_trees,
                pn.Row(pn.pane.HTML("Options", width=30), self.options_doc),
                self.x_axis,
                self.y_axis,
                self.y_ticks,
                self.sites_mutations,
                self.pack_unselected,
                self.param.symbol_size,
                self.param.node_labels,
                self.param.additional_options,
                collapsed=True,
                title="Advanced plotting options",
                header_background=config.SIDEBAR_BACKGROUND,
                active_header_background=config.SIDEBAR_BACKGROUND,
                styles=config.VCARD_STYLE,
            ),
            self.advanced_warning,
        )
        return sidebar_content


class TreesPage(View):
    key = "trees"
    title = "Trees"
    data = param.ClassSelector(class_=Tree)

    def __init__(self, **params):
        super().__init__(**params)
        self.data = Tree(datastore=self.datastore)
        self.sample_sets = self.datastore.sample_sets_table

    def __panel__(self):
        return pn.Column(
            self.data,
        )

    def sidebar(self):
        return pn.Column(
            pn.pane.HTML(
                "<h2 style='margin: 0;'>Trees</h2>",
                sizing_mode="stretch_width",
            ),
            pn.pane.Markdown(
                (
                    "This section allows you to explore local genealogical "
                    "trees.<br><br>"
                    "Use the controls below to customize the plots and adjust"
                    "parameters."
                ),
                sizing_mode="stretch_width",
            ),
            self.data.sidebar,
            self.data.advanced_options,
            self.sample_sets.sidebar_table,
        )
