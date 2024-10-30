import pytest

from tseda import datastore
from tseda.vpages import ignn


@pytest.fixture
def ds(tsbm):
    individuals_table, sample_sets_table = datastore.preprocess(tsbm)
    return datastore.DataStore(
        tsm=tsbm,
        individuals_table=individuals_table,
        sample_sets_table=sample_sets_table,
    )


@pytest.fixture
def vbar(ds):
    return ignn.VBar(datastore=ds)


@pytest.fixture
def hapgnn(ds):
    return ignn.GNNHaplotype(datastore=ds)


def test_gnn(vbar):
    df = vbar.gnn()
    print(df)


def test_haplotype_gnn(hapgnn):
    df = hapgnn.datastore.haplotype_gnn(0)
    print(df)
