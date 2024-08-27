import geopandas


def test_geo(tsm):
    gdf = tsm.get_individuals(astype="gdf")
    assert isinstance(gdf, geopandas.GeoDataFrame)
