from . import (
    gnn,  # noqa: F401
    overview,  # noqa: F401
    sample_sets,  # noqa: F401
)

PAGES_MAP = {
    "Overview": overview,
    "Sample set editor": sample_sets,
    "GNN": gnn,
}
