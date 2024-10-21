import pytest

from tseda import datastore
from tseda.vpages import gnn


@pytest.fixture(scope="module")
def ds(tsbm):
    individuals_table, sample_sets_table = datastore.preprocess(tsbm)
    return datastore.DataStore(
        tsm=tsbm,
        individuals_table=individuals_table,
        sample_sets_table=sample_sets_table,
    )


@pytest.fixture(scope="module")
def vbar(ds):
    return gnn.VBar(datastore=ds)


@pytest.fixture(scope="module")
def hapgnn(ds):
    return gnn.GNNHaplotype(datastore=ds)


def test_gnn(vbar):
    df = vbar.gnn()
    print(df)


def test_haplotype_gnn(hapgnn):
    df = hapgnn.datastore.haplotype_gnn(0)
    print(df)
