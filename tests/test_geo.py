import geopandas


def test_geo(ds):
    df = ds.individuals_table.data.rx.value
    df = df.loc[df.selected]
    gdf = geopandas.GeoDataFrame(
        df.drop(["longitude", "latitude"], axis=1),
        geometry=geopandas.points_from_xy(df.longitude, df.latitude),
    )
    assert isinstance(gdf, geopandas.GeoDataFrame)
