import geopandas
import hvplot.pandas  # noqa
import panel as pn
import param
import xyzservices.providers as xyz

from tseda import config

from .core import View

tiles_options = {
    "WorldImagery": xyz.Esri.WorldImagery,
    "WorldTopoMap": xyz.Esri.WorldTopoMap,
    "WorldStreetMap": xyz.Esri.WorldStreetMap,
    "WorldTerrain": xyz.Esri.WorldTerrain,
    "WorldShadedRelief": xyz.Esri.WorldShadedRelief,
    "WorldPhysical": xyz.Esri.WorldPhysical,
    "WorldGrayCanvas": xyz.Esri.WorldGrayCanvas,
}


class GeoMap(View):
    height = param.Integer(default=400, doc="Height of the map")
    width = param.Integer(default=1200, doc="Width of the map")

    tiles_selector = param.Selector(
        default="WorldPhysical",
        objects=list(tiles_options.keys()),
        doc="Select XYZ tiles for map",
    )
    tiles = tiles_options[tiles_selector.default]

    @pn.depends("tiles_selector", "height", "width")
    def __panel__(self):
        self.tiles = tiles_options[self.tiles_selector]
        df = self.datastore.individuals_table.data.rx.value
        df = df.loc[df.selected]
        color = self.datastore.color
        gdf = geopandas.GeoDataFrame(
            df.drop(["longitude", "latitude"], axis=1),
            geometry=geopandas.points_from_xy(df.longitude, df.latitude),
        )
        color = color.loc[~gdf.geometry.is_empty.values]
        gdf = gdf[~gdf.geometry.is_empty]
        return gdf.hvplot.points(
            hover_cols=["id", "name", "population", "sample_set_id"],
            geo=True,
            tiles=self.tiles,
            tiles_opts={"alpha": 0.5},
            width=self.width,
            height=self.height,
            size=100,
            color=color,
            tools=["wheel_zoom", "box_select", "tap", "pan", "reset"],
            fill_alpha=0.5,
            line_color="black",
        )

    def sidebar(self):
        return pn.Card(
            self.param.tiles_selector,
            self.param.height,
            self.param.width,
            collapsed=True,
            title="Map options",
            styles=config.VCARD_STYLE,
        )
