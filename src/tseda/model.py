import dataclasses
import json
import re
from enum import Enum

import daiquiri
import geopandas
import numpy as np
import pandas as pd
import tskit
from bokeh.palettes import Set3
from tsqc.model import TSModel

logger = daiquiri.getLogger("tseda")


class DataTypes(Enum):
    """
    Enum for getter method data types
    """

    LIST = "list"
    DATAFRAME = "df"
    GEO_DATAFRAME = "gdf"


def decode_metadata(obj):
    if not hasattr(obj, "metadata"):
        return None
    if isinstance(obj.metadata, bytes):
        return json.loads(obj.metadata.decode())
    return obj.metadata


def parse_metadata(obj, regex):
    """Retrieve metadata value pairs based on key regex"""
    md = decode_metadata(obj)
    key = list(filter(lambda x: regex.match(x), md.keys()))
    if len(key) >= 1:
        return md.get(key[0])
    return None


def palette(cmap=Set3[12], n=12, start=0, end=1):
    import matplotlib

    linspace = np.linspace(start, end, n)
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "customcmap", cmap
    )
    palette = cmap(linspace)
    hex_palette = [matplotlib.colors.rgb2hex(c) for c in palette]
    return hex_palette


@dataclasses.dataclass
class SampleSet:
    """
    A class to contain sample sets.
    """

    name_re = re.compile(r"^(name|Name|population|Population)$")

    id: np.int32
    name: str = None
    color: str = None
    population: dataclasses.InitVar[tskit.Population | None] = None

    colormap = palette()

    def __post_init__(self, population):
        if self.color is None:
            self.color = self.colormap[self.id % len(self.colormap)]
        if population is not None:
            self.name = parse_metadata(population, self.name_re)
        if self.name is None:
            self.name = f"SampleSet-{self.id}"


@dataclasses.dataclass
class Individual(tskit.Individual):
    """
    A class to handle individuals.
    """

    name_re = re.compile(r"^(name|Name|SM)$")
    longitude_re = re.compile(r"^(longitude|Longitude|lng|long)$")
    latitude_re = re.compile(r"^(latitude|Latitude|lat)$")

    population: np.int32 = None
    longitude: np.float64 = None
    latitude: np.float64 = None
    name: str = None
    sample_set_id: np.int32 = None
    selected: bool = True

    def __init__(self, individual: tskit.Individual):
        super().__init__(
            id=individual.id,
            flags=individual.flags,
            location=individual.location,
            metadata=individual.metadata,
            nodes=individual.nodes,
            parents=individual.parents,
        )
        self.population = individual.population
        self.sample_set_id = self.population
        self.__post_init__()

    def __post_init__(self) -> None:
        self.longitude = parse_metadata(self, self.longitude_re)
        self.latitude = parse_metadata(self, self.latitude_re)
        self.name = parse_metadata(self, self.name_re)

    @property
    def samples(self):
        return self.nodes

    def toggle(self) -> None:
        self.selected = not self.selected

    def select(self) -> None:
        self.selected = True

    def deselect(self) -> None:
        self.selected = False


@dataclasses.dataclass
class Sample(tskit.Node):
    """A class to handle samples."""

    sample_set_id: np.int32 = None
    selected: bool = True

    def __init__(self, node: tskit.Node):
        super().__init__(
            id=node.id,
            flags=node.flags,
            time=node.time,
            population=node.population,
            individual=node.individual,
            metadata=node.metadata,
        )
        self.__post_init__()

    def __post_init__(self) -> None:
        self.sample_set_id = self.population

    def toggle(self) -> None:
        self.selected = not self.selected

    def select(self) -> None:
        self.selected = True

    def deselect(self) -> None:
        self.selected = False


# TODO: add relevant methods to caching. Cache id should be calculated
# with respect to the selected sample sets
class TSEdaModel(TSModel):
    """Tree sequence eda model"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sample_sets = [
            SampleSet(id=pop.id, population=pop)
            for pop in self.ts.populations()
        ]
        # TODO: Make hidden and write properties to filter on
        # selected/deselected?
        self.individuals = self._init_individuals()
        self.samples = self._init_samples()

    def _init_individuals(self):
        result = []
        for ts_ind in self.ts.individuals():
            ind = Individual(individual=ts_ind)
            result.append(ind)
        return result

    def _init_samples(self):
        result = []
        for ts_ind in self.ts.individuals():
            for node in ts_ind.nodes:
                sample = Sample(self.ts.node(node))
                result.append(sample)
        return result

    def _get_data(self, attr="individuals", astype="list", deselected=True):
        if deselected:
            data = self.__getattribute__(attr)
        else:
            data = [d for d in self.__getattribute__(attr) if d.selected]
        if astype == "list":
            return data
        if astype == DataTypes.DATAFRAME.value:
            df = pd.DataFrame(data)
            return df
        elif astype == DataTypes.GEO_DATAFRAME.value:
            df = pd.DataFrame(data)
            return geopandas.GeoDataFrame(
                df.drop(["longitude", "latitude"], axis=1),
                geometry=geopandas.points_from_xy(df.longitude, df.latitude),
            )

    def get_individuals(self, astype="list", deselected=True):
        """
        Returns a list / DataFrame / GeoDataFrame of individuals.
        """
        data = self._get_data("individuals", astype, deselected)
        if isinstance(data, list):
            return data
        return data.set_index(["id"])

    def get_samples(self, astype="list", deselected=True):
        """
        Returns a list / DataFrame of samples.
        """
        if astype == DataTypes.GEO_DATAFRAME.value:
            raise ValueError("geo data frame not supported for samples")
        data = self._get_data("samples", astype, deselected)
        if isinstance(data, list):
            return data
        return data.set_index(["id"])

    def update_individual_sample_set(self, ind_id, sample_set_id):
        self.individuals[ind_id].sample_set_id = sample_set_id
        for sid in self.individuals[ind_id].samples:
            self.samples[sid].sample_set_id = sample_set_id

    def toggle_individual(self, ind_id):
        self.individuals[ind_id].toggle()
        for sid in self.individuals[ind_id].samples:
            self.samples[sid].toggle()

    def deselect_individual(self, ind_id):
        self.individuals[ind_id].deselect()
        for sid in self.individuals[ind_id].samples:
            self.samples[sid].deselect()

    def select_individual(self, ind_id):
        self.individuals[ind_id].select()
        for sid in self.individuals[ind_id].samples:
            self.samples[sid].select()

    def make_sample_sets(self):
        """Make sample sets"""
        sample_sets = {}
        samples = []
        for sample in self.samples:
            if not sample.selected:
                continue
            samples.append(sample.id)
            if sample.sample_set_id not in sample_sets:
                sample_sets[sample.sample_set_id] = []
            sample_sets[sample.sample_set_id].append(sample.id)
        return samples, sample_sets

    # TODO: make cached_property
    def gnn(self):
        """
        Returns a GNN object for the tree sequence
        """
        samples, sample_sets = self.make_sample_sets()
        gnn = self.ts.genealogical_nearest_neighbours(
            samples, sample_sets=list(sample_sets.values())
        )
        df = pd.DataFrame(
            gnn,
            columns=[i for i in sample_sets],  # pyright: ignore
        )
        df["sample_set_id"] = [self.samples[i].sample_set_id for i in samples]
        df["id"] = [self.samples[i].individual for i in samples]
        df["sample_id"] = df.index
        df.set_index(["sample_set_id", "sample_id", "id"], inplace=True)
        return df

    def colormap(self, by_sample=False, deselected=True):
        """
        Get colormap for individuals or samples
        """
        result = []
        if by_sample:
            data = self.get_samples(deselected=deselected)
        else:
            data = self.get_individuals(deselected=deselected)
        for d in data:
            result.append(self.sample_sets[d.sample_set_id].color)
        return np.array(result)
