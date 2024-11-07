"""Genealogical Nearest Neighbors (GNN) analysis, individual haplotype
plots.

Draw GNN proportions for a selected individual over the haplotypes.


TODO:

- this code works but needs a lot of cleaning up and simplification
- move common make_windows function to a common place (see .stats)
- hvplot bar plot is not working as expected, need to investigate, but
  area plot could be used instead
- for larger datasets, the underlying computation is slow, so either
  needs caching or async processing
"""

import holoviews as hv
import hvplot.pandas  # noqa
import numpy as np
import panel as pn
import param

hv.extension("bokeh")


def make_windows(window_size, sequence_length):
    """Make windows for statistics."""
    num_windows = int(sequence_length / window_size)
    windows = np.linspace(0, sequence_length, num_windows + 1)
    windows[-1] = sequence_length
    return windows


class GNNHaplotype(param.Parameterized):
    individual_id = param.Integer(
        default=None,
        bounds=(0, None),
        doc="Individual ID (0-indexed)",
    )
    window_size = param.Integer(
        default=10000, bounds=(1, None), doc="Size of window"
    )

    def __init__(self, tsm, **kwargs):
        super().__init__(**kwargs)
        self.tsm = tsm
        self._data = None

    def plot(self, haplotype=0):
        if self.window_size is not None:
            windows = make_windows(
                self.window_size, self.tsm.ts.sequence_length
            )
        else:
            windows = None

        self._data = self.tsm.haplotype_gnn(
            self.individual_id, windows=windows
        )
        df = self._data.loc[
            self._data.index.get_level_values("haplotype") == haplotype
        ]
        df = df.droplevel(["haplotype", "end"])
        populations = df.columns
        df.reset_index(inplace=True)
        colormap = [
            self.tsm.get_sample_set_by_name(x).color for x in populations
        ]
        return df.hvplot.area(
            x="start",
            y=populations,
            color=colormap,
            legend="right",
            fill_alpha=0.5,
            min_width=800,
            min_height=300,
            responsive=True,
        )

    @param.depends("individual_id", "window_size")
    def panel(self):
        if self.individual_id is None:
            return pn.Column()
        self._data = self.tsm.haplotype_gnn(self.individual_id)
        return pn.Column(
            self.plot(0),
            self.plot(1),
        )


def page(tsm):
    md = pn.pane.Markdown(
        """
        ## GNN haplotype plots

        
        """
    )

    gnn = GNNHaplotype(tsm)
    return pn.Column(md, gnn.param, gnn.panel)
