import numpy as np
import pytest

from tseda import datastore


@pytest.fixture(scope="module")
def ds(tsbm):
    individuals_table, sample_sets_table = datastore.preprocess(tsbm)
    return datastore.DataStore(
        tsm=tsbm,
        individuals_table=individuals_table,
        sample_sets_table=sample_sets_table,
    )


@pytest.fixture(scope="module")
def individuals_table(tsbm):
    data, _ = datastore.preprocess(tsbm)
    return data


def test_datastore_preprocess(tsbm):
    individuals_table, sample_sets_table = datastore.preprocess(tsbm)
    assert individuals_table is not None
    assert sample_sets_table is not None
    samples, sample_sets = individuals_table.sample_sets()
    assert len(sample_sets) == 6
    np.testing.assert_equal(sample_sets[1], np.arange(0, 12))


def test_individuals_table(individuals_table):
    data = individuals_table.table
    print(individuals_table.loc(5))


def test_datastore(ds):
    print(ds.color)
    print(ds.sample_sets_table.color_by_name)
