import random

import daiquiri
import pandas as pd
import panel as pn
import param
from panel.viewable import Viewer
from tsbrowse import model

from tseda import config
from tseda.model import Individual, SampleSet

from .gnn import windowed_genealogical_nearest_neighbours

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
        ss = SampleSet(id=ts_pop.id, population=ts_pop, predefined=True)
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


class SampleSetsTable(Viewer):
    default_columns = ["name", "color", "predefined"]
    editors = {k: None for k in default_columns}
    editors["color"] = {
        "type": "list",
        "values": config.COLORS,
        "valueLookup": True,
    }
    editors["name"] = {"type": "input", "validator": "unique", "search": True}
    formatters = {
        "color": {"type": "color"},
        "predefined": {"type": "tickCross"},
    }

    create_sample_set_textinput = param.String(
        doc="Enter name of new sample set. Press Enter (⏎) to create.",
        default=None,
        label="Create new sample set",
    )

    sample_set_warning = pn.pane.Alert(
        "This sample set name already exists, pick a unique name.",
        alert_type="warning",
        visible=False,
    )

    page_size = param.Selector(objects=[10, 20, 50, 100], default=20)

    table = param.DataFrame()

    def __init__(self, **params):
        super().__init__(**params)
        self.table.set_index(["id"], inplace=True)
        self.data = self.param.table.rx()

    @property
    def tooltip(self):
        return pn.widgets.TooltipIcon(
            value=(
                "The name and color of each sample set are editable. In the "
                "color column, select a color from the dropdown list. In the "
                "individuals table, you can assign individuals to sample sets."
            ),
        )

    @pn.depends("page_size", "create_sample_set_textinput")  # , "columns")
    def __panel__(self):
        if self.create_sample_set_textinput is not None:
            previous_names = [
                self.table.name[i] for i in range(len(self.table))
            ]
            if self.create_sample_set_textinput in previous_names:
                self.sample_set_warning.visible = True
            else:
                previous_colors = [
                    self.table.color[i] for i in range(len(self.table))
                ]
                unused_colors = [
                    color
                    for color in config.COLORS
                    if color not in previous_colors
                ]
                if len(unused_colors) != 0:
                    colors = unused_colors
                else:
                    colors = config.COLORS
                self.sample_set_warning.visible = False
                i = max(self.param.table.rx.value.index) + 1
                self.param.table.rx.value.loc[i] = [
                    self.create_sample_set_textinput,
                    colors[random.randint(0, len(colors) - 1)],
                    False,
                ]
                self.create_sample_set_textinput = None
        table = pn.widgets.Tabulator(
            self.data,
            layout="fit_data_table",
            selectable=True,
            page_size=self.page_size,
            pagination="remote",
            margin=10,
            formatters=self.formatters,
            editors=self.editors,
        )
        return pn.Column(
            pn.pane.Markdown("### Sample Set Table"), self.tooltip, table
        )

    def sidebar_table(self):
        table = pn.widgets.Tabulator(
            self.data,
            layout="fit_data_table",
            selectable=True,
            page_size=10,
            pagination="remote",
            margin=10,
            formatters=self.formatters,
            editors=self.editors,
            hidden_columns=["id"],
        )
        return pn.Card(
            pn.Column(self.tooltip, table),
            title="Sample sets table quick view",
            collapsed=True,
            header_background=config.SIDEBAR_BACKGROUND,
            active_header_background=config.SIDEBAR_BACKGROUND,
            styles=config.VCARD_STYLE,
        )

    def sidebar(self):
        return pn.Column(
            pn.Card(
                self.param.page_size,
                self.param.create_sample_set_textinput,
                title="Sample sets table options",
                collapsed=False,
                header_background=config.SIDEBAR_BACKGROUND,
                active_header_background=config.SIDEBAR_BACKGROUND,
                styles=config.VCARD_STYLE,
            ),
            self.sample_set_warning,
        )

    @property
    def color(self):
        """Return the color of all sample sets as a dictionary"""
        d = {}
        for index, row in self.data.rx.value.iterrows():
            d[index] = row.color
        return d

    @property
    def color_by_name(self):
        """Return the color of all sample sets as a dictionary with
        sample set names as keys"""
        d = {}
        for _, row in self.data.rx.value.iterrows():
            d[row["name"]] = row.color
        return d

    @property
    def names(self):
        """Return the names of all sample sets as a dictionary"""
        d = {}
        for index, row in self.data.rx.value.iterrows():
            d[index] = row["name"]
        return d

    @property
    def names2id(self):
        """Return the sample sets as dictionary with names as keys,
        ids as values"""
        d = {}
        for index, row in self.data.rx.value.iterrows():
            d[row["name"]] = index
        return d

    def loc(self, i):
        """Return sample set by index"""
        return self.data.rx.value.loc[i]


class DataStore(Viewer):
    tsm = param.ClassSelector(class_=model.TSModel)
    individuals_table = param.ClassSelector(class_=IndividualsTable)
    sample_sets_table = param.ClassSelector(class_=SampleSetsTable)

    views = param.List(constant=True)

    @property
    def color(self):
        """Return colors of selected individuals"""
        color = pd.merge(
            self.individuals_table.data.rx.value,
            self.sample_sets_table.data.rx.value,
            left_on="sample_set_id",
            right_index=True,
        )
        return color.loc[color.selected].color

    def haplotype_gnn(self, focal_ind, windows=None):
        sample_sets = self.individuals_table.sample_sets()
        ind = self.individuals_table.loc(focal_ind)
        hap = windowed_genealogical_nearest_neighbours(
            self.tsm.ts, ind.nodes, sample_sets, windows=windows
        )
        dflist = []
        sample_set_names = [
            self.sample_sets_table.loc(i)["name"] for i in sample_sets
        ]
        if windows is None:
            for i in range(hap.shape[0]):
                x = pd.DataFrame(hap[i, :])
                x = x.T
                x.columns = sample_set_names
                x["haplotype"] = i
                x["start"] = 0
                x["end"] = self.tsm.ts.sequence_length
                dflist.append(x)
        else:
            for i in range(hap.shape[1]):
                x = pd.DataFrame(hap[:, i, :])
                x.columns = sample_set_names
                x["haplotype"] = i
                x["start"] = windows[0:-1]
                x["end"] = windows[1:]
                dflist.append(x)
        df = pd.concat(dflist)
        df.set_index(["haplotype", "start", "end"], inplace=True)
        return df

    # Not needed? Never used?
    def __panel__(self):
        return pn.Row(
            self.individuals_table,
            self.sample_sets_table,
        )
