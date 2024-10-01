from . import (
    gnn,  # noqa: F401
    gnnhaplotype,  # noqa: F401
    overview,  # noqa: F401
    sample_sets,  # noqa: F401
    stats,  # noqa: F401
    structure,  # noqa: F401
    trees,  # noqa: F401
)

PAGES = [
    overview.OverviewPage,
    sample_sets.SampleSetsPage,
    structure.StructurePage,
    stats.StatsPage,
    gnn.GNNPage,
    trees.TreesPage,
]

PAGES_MAP = {page.key: page for page in PAGES}
PAGES_BY_TITLE = {page.title: page for page in PAGES}
