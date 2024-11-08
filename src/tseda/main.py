"""Helper module for serving the TSEda app from the command line using
panel serve.

This module is used to serve the TSEda app from the command line using
panel serve. One use case is for development purposes where the --dev
argument enables automated reloading of the app when the source code
changes. To launch the app from the command line run:

    $ panel serve --dev --admin --show --args path/to/tszip_file.zip

See https://panel.holoviz.org/how_to/server/commandline.html for more
information.
"""

from tseda import app  # noqa
from tseda import datastore  # noqa
from tsbrowse.model import TSModel  # noqa
import daiquiri
import sys

daiquiri.setup(level="WARN")  # noqa
logger = daiquiri.getLogger("tseda")


if len(sys.argv) < 2:
    logger.error(
        "Please provide the path to a TreeSequence file via the --args option."
    )
    sys.exit(1)

path = sys.argv.pop()

tsm = TSModel(path)
individuals_table, sample_sets_table = datastore.preprocess(tsm)

app_ = app.DataStoreApp(
    datastore=datastore.DataStore(
        tsm=tsm,
        individuals_table=individuals_table,
        sample_sets_table=sample_sets_table,
    ),
    title="TSEda Datastore App",
    views=[datastore.IndividualsTable],
)

app_.view().servable()
