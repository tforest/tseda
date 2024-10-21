import holoviews as hv
import hvplot.pandas  # noqa
import pandas as pd
import panel as pn

# from .gnnhaplotype import GNNHaplotype
import param
from bokeh.models import (
    ColumnDataSource,
    FactorRange,
    HoverTool,
)
from bokeh.plotting import figure

from .core import View
from .map import GeoMap

hv.extension("bokeh")
pn.extension(sizing_mode="stretch_width")


def make_sample_sets(inds):
    sample_sets = {}
    samples = []
    for _, ind in inds.iterrows():
        sample_set = ind.sample_set_id
        if sample_set not in sample_sets:
            sample_sets[sample_set] = []
        sample_sets[sample_set].append(ind.id)
        samples.append(ind.id)
    return sample_sets


class VBar(View):
    """Make VBar plot of GNN output."""

    sort_order = param.List(
        default=[],
        item_type=str,
        doc=(
            "Change sort order within sample sets. Default is "
            "to sort by sample index. Provide a list of strings "
            "where items correspond to sample set names."
        ),
    )

    def gnn(self):
        inds = self.datastore.individuals_table.data.rx.value
        samples, sample_sets = self.datastore.individuals_table.sample_sets()
        gnn = self.datastore.tsm.ts.genealogical_nearest_neighbours(
            samples, sample_sets=list(sample_sets.values())
        )
        df = pd.DataFrame(
            gnn,
            columns=[i for i in sample_sets],
        )
        df["sample_set_id"] = [
            inds.loc[inds.id.loc[i]].sample_set_id for i in samples
        ]
        df["id"] = [inds.loc[inds.id.loc[i]].id for i in samples]
        df["sample_id"] = df.index
        df.set_index(["sample_set_id", "sample_id", "id"], inplace=True)
        return df

    def __panel__(self):
        df = self.gnn()
        sample_sets = self.datastore.sample_sets_table.data.rx.value
        color = self.datastore.color
        table = pn.widgets.Tabulator(
            df,
            layout="fit_columns",
            height=400,
            pagination="remote",
            page_size=10,
            theme="midnight",
        )
        return table
        # return pn.Column(self.plot)

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     self.tsm = self.datastore.tsm
    #     table = self.datastore.individuals_table
    #     inds = table.table.loc[table.table.selected]
    #     print(inds.shape)
    #     self._data = inds
    # self._data = self.tsm.gnn()
    # self._color = [
    #     self.tsm.sample_sets[i].color for i in self._data.columns
    # ]
    # self._groups = [
    #     self.tsm.sample_sets[i].name for i in self._data.columns
    # ]
    # self._levels = self._data.index.names
    # self._factors = list(
    #     tuple([tsm.sample_sets[x[0]].name, str(x[1])])
    #     for x in self._data.index
    # )
    # self._data.columns = self.groups
    # self._data.reset_index(inplace=True)
    # self._data["x"] = self.factors
    # self._data["name"] = [
    #     tsm.individuals[self._data["id"][x]].name for x in self._data.index
    # ]

    @property
    def data(self):
        return self._data

    @property
    def color(self):
        """Color mapping for groups"""
        return self._color

    @property
    def groups(self):
        """Group (sample sets) names"""
        return self._groups

    @property
    def levels(self):
        """Sample index levels"""
        return self._levels

    @property
    def factors(self):
        """Factors consist of 2-tuples that correspond to
        (individual, population) grouping"""
        return self._factors

    @param.depends("sort_order")
    def plot(self):
        """Make vbar plot. Holoviews does not support grouping by default
        so we need to implement it using low-level bokeh API."""
        hover = HoverTool()
        hover.tooltips = list([("name", "@name")])
        hover.tooltips.extend(list(map(lambda x: (x, f"@{x}"), self.levels)))
        hover.tooltips.extend(
            list(
                map(
                    lambda x: (x, f"@{x}{{%0.1f}}"),
                    self.groups,
                )
            )
        )

        data = self.data
        if len(self.sort_order) > 0:
            sort_order = (
                ["sample_set_id"] + self.sort_order + ["sample_id", "id"]
            )
            data.sort_values(sort_order, axis=0, inplace=True)
            self._factors = data["x"].values
        source = ColumnDataSource(data)
        self._fig = figure(
            x_range=FactorRange(
                *self.factors, group_padding=0.1, subgroup_padding=0
            ),
            height=400,
            sizing_mode="stretch_width",
            tools="xpan,xwheel_zoom,box_select,save,reset",
        )
        self._fig.add_tools(hover)
        self._fig.vbar_stack(
            self.groups,
            source=source,
            x="x",
            color=self.color,
            legend_label=self.groups,
            width=1,
            line_color="black",
            line_alpha=0.7,
            line_width=0.5,
            fill_alpha=0.5,
        )

        self._fig.add_layout(self._fig.legend[0], "right")
        self._fig.legend[0].label_text_font_size = "12pt"

        self._fig.axis.major_tick_line_color = None
        self._fig.axis.minor_tick_line_color = None
        self._fig.xaxis.group_label_orientation = 1.0
        self._fig.xaxis.subgroup_label_orientation = 1.0
        self._fig.xaxis.group_text_font_size = "14pt"
        self._fig.xaxis.major_label_orientation = 1.0
        self._fig.xaxis.major_label_text_font_size = "0pt"
        self._fig.yaxis.major_label_text_font_size = "12pt"
        self._fig.yaxis.axis_label_text_font_size = "14pt"
        self._fig.axis.axis_line_color = None
        self._fig.grid.grid_line_color = None
        self._fig.outline_line_color = "black"
        self._fig.xaxis.separator_line_width = 2.0
        self._fig.xaxis.separator_line_color = "grey"
        self._fig.xaxis.separator_line_alpha = 0.5

        return self._fig


class GNNPage(View):
    key = "GNN"
    title = "GNN analysis"
    geomap = param.ClassSelector(class_=GeoMap)
    vbar = param.ClassSelector(class_=VBar)

    def __init__(self, **params):
        super().__init__(**params)
        self.geomap = GeoMap(datastore=self.datastore)
        self.vbar = VBar(datastore=self.datastore)

    def __panel__(self):
        return pn.Column(self.geomap, self.vbar)

    def sidebar(self):
        return pn.Column(
            pn.pane.Markdown("## GNN"),
            self.geomap.param.tiles_selector,
            self.geomap.param.height,
            self.geomap.param.width,
        )
