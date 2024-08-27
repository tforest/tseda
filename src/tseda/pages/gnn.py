import hvplot.pandas  # noqa
import panel as pn
import holoviews as hv
import xyzservices.providers as xyz
from bokeh.plotting import figure
from bokeh.models import (
    FactorRange,
    ColumnDataSource,
    HoverTool,
    BoxSelectTool,
)

hv.extension("bokeh")


def setup_vbar_data(tsm):
    data = tsm.gnn()
    color = [tsm.sample_sets[i].color for i in data.columns]
    groups = [tsm.sample_sets[i].name for i in data.columns]
    data.columns = groups

    levels = data.index.names
    factors = list(
        tuple([tsm.sample_sets[x[0]].name, str(x[1])]) for x in data.index
    )
    data.reset_index(inplace=True)
    data["x"] = factors
    data["name"] = [tsm.individuals[data["id"][x]].name for x in data.index]
    return data, levels, groups, color


def setup_geomap_data(tsm):
    gdf = tsm.get_individuals(astype="gdf")[
        ["sample_set_id", "population", "geometry"]
    ]
    gdf = gdf.reset_index().set_index(["id", "sample_set_id", "population"])
    colormap = tsm.colormap()[~gdf.geometry.is_empty]
    return gdf[~gdf.geometry.is_empty], colormap


def vbar(source, levels, groups, color, factors):
    """Make vbar plot. Holoviews does not support grouping by default
    so we need to implement it using low-level bokeh API."""
    # Bars plot
    # source = ColumnDataSource(data)
    # factors = data["x"]
    bars = figure(
        x_range=FactorRange(*factors, group_padding=0.1, subgroup_padding=0),
        width=1200,
        height=300,
    )

    bars.vbar_stack(
        groups,
        source=source,
        x="x",
        color=color,
        legend_label=groups,
        width=1,
        line_color="black",
        line_alpha=0.7,
        line_width=0.5,
        fill_alpha=0.5,
    )

    bars.add_layout(bars.legend[0], "right")
    bars.legend[0].label_text_font_size = "12pt"

    hover = HoverTool()
    hover.tooltips = list(
        map(lambda x: (x[0], f"@{x[1]}"), zip(levels, levels))
    )
    hover.tooltips.extend(
        list(map(lambda x: (x[0], f"@{x[1]}{{%0.1f}}"), zip(groups, groups)))
    )
    bars.add_tools(hover)
    bars.add_tools(BoxSelectTool())

    bars.axis.major_tick_line_color = None
    bars.axis.minor_tick_line_color = None
    bars.xaxis.group_label_orientation = 1.0
    bars.xaxis.subgroup_label_orientation = 1.0
    bars.xaxis.group_text_font_size = "14pt"
    bars.xaxis.major_label_orientation = 1.0
    bars.xaxis.major_label_text_font_size = "0pt"
    bars.yaxis.major_label_text_font_size = "12pt"
    bars.yaxis.axis_label_text_font_size = "14pt"
    bars.axis.axis_line_color = None
    bars.grid.grid_line_color = None
    bars.outline_line_color = "black"
    bars.xaxis.separator_line_width = 0.0
    return bars


def world_map(gdf, colormap):
    """Make world map plot"""
    # return gdf[~gdf.geometry.is_empty].hvplot.points(
    return gdf.hvplot.points(
        hover_cols=["id", "population", "sample_set_id"],
        geo=True,
        tiles=xyz.Esri.WorldPhysical,
        tiles_opts={"alpha": 0.5},
        width=1200,
        height=600,
        size=100,
        color=colormap,
        tools=["wheel_zoom", "box_select", "tap", "pan", "reset"],
        fill_alpha=0.5,
        line_color="black",
    )


def page(tsm):
    geomap_df, colormap = setup_geomap_data(tsm)
    bars_df, levels, groups, color = setup_vbar_data(tsm)

    geomap = world_map(geomap_df, colormap)
    bars_df_source = ColumnDataSource(bars_df)
    factors = bars_df["x"]
    bars = vbar(bars_df_source, levels, groups, color, factors)

    # bars_df_source.selected.on_change("indices", callback)
    # selection = hv.streams.Selection1D(source=[])

    # def callback(attr, old, new):
    #     selection.source = new

    # def dynamic_map(index):
    #     selected_df = geomap_df.iloc[index]
    #     return selected_df

    # dmap = hv.DynamicMap(dynamic_map, streams=[selection])

    return pn.Column(geomap, bars)
