from . import (
    gnn,
    individuals,
    overview,
    sample_sets,
    stats,
    trees,
)

PAGES = [
    overview.OverviewPage,
    sample_sets.SampleSetsPage,
    individuals.IndividualsPage,
    gnn.GNNPage,
    stats.StatsPage,
    trees.TreesPage,
]

PAGES_MAP = {page.key: page for page in PAGES}
PAGES_BY_TITLE = {page.title: page for page in PAGES}
