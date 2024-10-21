from . import (
    gnn,
    individuals,
    overview,
    sample_sets,
)

PAGES = [
    overview.OverviewPage,
    sample_sets.SampleSetsPage,
    individuals.IndividualsPage,
    gnn.GNNPage,
]

PAGES_MAP = {page.key: page for page in PAGES}
PAGES_BY_TITLE = {page.title: page for page in PAGES}
