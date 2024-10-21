import daiquiri
import pandas as pd
import panel as pn
import param
from panel.viewable import Viewer
from tsbrowse import model

from tseda.model import Individual, SampleSet

logger = daiquiri.getLogger("tseda")


def make_individuals_table(tsm):
    result = []
    for ts_ind in tsm.ts.individuals():
        ind = Individual(individual=ts_ind)
        result.append(ind)
    return IndividualsTable(table=pd.DataFrame(result))


def make_sample_sets_table(tsm):
    result = []
    for ts_pop in tsm.ts.populations():
        ss = SampleSet(id=ts_pop.id, population=ts_pop, immutable_id=True)
        result.append(ss)
    return SampleSetsTable(table=pd.DataFrame(result))


def preprocess(tsm):
    """Take a tsbrowse.TSModel and make individuals and sample sets tables."""
    logger.info(
        "Preprocessing data: making individuals and sample sets tables"
    )
    individuals_table = make_individuals_table(tsm)
    sample_sets_table = make_sample_sets_table(tsm)
    return individuals_table, sample_sets_table


class IndividualsTable(Viewer):
    """Class to hold and view individuals and perform calculations to
    change filter."""

    columns = [
        "id",
        "name",
        "population",
        "sample_set_id",
        "selected",
        "longitude",
        "latitude",
    ]
    individuals_editors = {k: None for k in columns}
    individuals_editors["sample_set_id"] = {
        "type": "list",
        "values": [],
        "valueLookup": True,
    }
    individuals_editors["selected"] = {
        "type": "list",
        "values": [False, True],
        "valuesLookup": True,
    }
    individuals_formatters = {"selected": {"type": "tickCross"}}

    table = param.DataFrame()

    page_size = param.Selector(
        objects=[10, 20, 50, 100, 200, 500],
        default=100,
        doc="Number of rows per page to display",
    )
    toggle = param.Integer(
        default=None, bounds=(0, None), doc="Toggle sample set by index"
    )
    population_from = param.Integer(
        default=None,
        bounds=(0, None),
        doc=(
            "Batch reassign individual from this `population` "
            "to the index given in the `sample_set_to` parameter"
        ),
    )
    sample_set_to = param.Integer(
        default=None,
        bounds=(0, None),
        doc=(
            "Batch reassign individuals in the index given in "
            "the `sample_set_from` parameter to this sample set. "
            "Update will only take place when both fields are set."
        ),
    )

    def __init__(self, **params):
        super().__init__(**params)
        self.data = self.param.table.rx()

    @property
    def tooltip(self):
        return pn.widgets.TooltipIcon(
            value=(
                "Individuals table with columns relevant for modifying plots. "
                "The `population_id` column is immutable and displays the  "
                "population id of the individual, as assigned during "
                "inference. The `sample_set_id` column is editable and can "
                "be assigned to a sample set id from the sample set table "
                "through a drop-down list by clicking on a cell. "
                "The `selected` column indicates whether an individual is  "
                "included in the analyses or not, and can be toggled to  "
                "exclude/include individuals of choice. Individuals lacking "
                "geolocation coordinates (`longitude`/`latitude`) are not  "
                "displayed in the GeoMap plots."
            ),
        )

    def sample_sets(self):
        sample_sets = {}
        samples = []
        inds = self.data.rx.value
        for _, ind in inds.iterrows():
            sample_set = ind.sample_set_id
            if sample_set not in sample_sets:
                sample_sets[sample_set] = []
            sample_sets[sample_set].append(ind.id)
            samples.append(ind.id)
        return samples, sample_sets

    @pn.depends("page_size", "toggle", "sample_set_to")
    def __panel__(self):
        if self.toggle is not None:
            # self.table.loc[self.toggle == self.table.sample_set_id, "selected"] = not self.table.loc[
            #     self.toggle, "selected"
            # ]
            self.data.rx.value.loc[
                self.toggle == self.data.rx.value.sample_set_id, "selected"
            ] = not self.data.rx.value.loc[self.toggle, "selected"]
            self.toggle = None
        if self.sample_set_to is not None:
            if self.population_from is not None:
                self.table.loc[
                    self.table["population"] == self.population_from,
                    "sample_set_id",
                ] = self.sample_set_to
            else:
                print("Nothing happening")
        data = self.data[self.columns]
        table = pn.widgets.Tabulator(
            data,
            pagination="remote",
            layout="fit_columns",
            selectable=True,
            page_size=self.page_size,
            formatters=self.individuals_formatters,
            editors=self.individuals_editors,
            margin=10,
            text_align={"selected": "center"},
        )
        return pn.Column(self.tooltip, table)


class SampleSetsTable(Viewer):
    table = param.DataFrame()

    def __init__(self, **params):
        super().__init__(**params)
        self.data = self.param.table.rx()

    def __panel__(self):
        return pn.Column(
            self.data,
        )


class DataStore(Viewer):
    tsm = param.ClassSelector(class_=model.TSModel)
    individuals_table = param.ClassSelector(class_=IndividualsTable)
    sample_sets_table = param.ClassSelector(class_=SampleSetsTable)

    views = param.List(constant=True)

    @property
    def color(self):
        color = pd.merge(
            self.individuals_table.data.rx.value,
            self.sample_sets_table.data.rx.value,
            left_on="sample_set_id",
            right_on="id",
        )
        return color.loc[color.selected].color

    # Not needed? Never used?
    def __panel__(self):
        return pn.Row(
            self.individuals_table,
            self.sample_sets_table,
        )
