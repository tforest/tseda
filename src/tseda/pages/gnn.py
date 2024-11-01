"""Genealogical Nearest Neighbors (GNN) analysis.

Draw GNN plots for individuals and haplotypes. The GNN plot shows the
GNN proportions in each sample set for each individual or haplotype.
The GNN proportions are calculated using the genealogical nearest
neighbors method.

Individuals are grouped and colored by sample set. The groupings and
colors can be modified in the sample set editor. Hovering over the bars
in the plot shows the GNN proportions of each sample set for a given
sample.

TODO:

- linked brushing between the map and the GNN plot
"""

import hvplot.pandas  # noqa
import panel as pn
import holoviews as hv
from bokeh.plotting import figure
from bokeh.models import (
    FactorRange,
    ColumnDataSource,
    HoverTool,
)
from .map import GeoMap
from .gnnhaplotype import GNNHaplotype

import param

hv.extension("bokeh")
pn.extension(sizing_mode="stretch_width")


class VBar(param.Parameterized):
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

    def __init__(self, tsm, **kwargs):
        super().__init__(**kwargs)
        self.tsm = tsm
        self._data = self.tsm.gnn()
        self._color = [
            self.tsm.sample_sets[i].color for i in self._data.columns
        ]
        self._groups = [
            self.tsm.sample_sets[i].name for i in self._data.columns
        ]
        self._levels = self._data.index.names
        self._factors = list(
            tuple([tsm.sample_sets[x[0]].name, str(x[1])])
            for x in self._data.index
        )
        self._data.columns = self.groups
        self._data.reset_index(inplace=True)
        self._data["x"] = self.factors
        self._data["name"] = [
            tsm.individuals[self._data["id"][x]].name for x in self._data.index
        ]

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
                ["sample_set_id"] + self.sort_order + ["sample_id", "id"]  # pyright: ignore[reportOperatorIssue]
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


class GNNPage:
    key = "GNN"
    title = "GNN analysis"

    def __init__(self, tsm):
        self.tsm = tsm
        self.geomap = GeoMap(tsm)
        self.vbar = VBar(tsm)
        self.hap = GNNHaplotype(tsm)

        self.content = pn.Column(
            self.geomap.plot,
            self.vbar.plot,
            self.hap.panel,
        )
        self.sidebar = pn.Column(
            pn.pane.Markdown("# GNN analysis options"),
            pn.Param(self.geomap.param, width=200),
            pn.Param(self.vbar.param, width=200),
            pn.Param(self.hap.param, width=200),
        )
