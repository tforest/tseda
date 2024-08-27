import matplotlib.colors as mcolors
import pandas as pd
import panel as pn

pn.extension("tabulator")

palette = list(mcolors.CSS4_COLORS.keys())

# TODO: function for multiselection widget
# def get_selected_data(selected_ids=None):
#     if selected_ids is not None:
#         for ind in tsm.individuals:
#             tsm.deselect_individual(ind.id)
#         for sid in selected_ids:
#             tsm.select_individual(sid)
#     df = tsm.get_individuals(astype="df", deselected=True)
#     return df[
#         [
#             "name",
#             "population",
#             "sample_set_id",
#             "selected",
#             "longitude",
#             "latitude",
#         ]
#     ]


def make_sample_sets_table(sample_sets_df):
    sample_editors = {}
    sample_editors["color"] = {
        "type": "list",
        "values": palette,
        "valueLookup": True,
    }
    sample_formatters = {"color": {"type": "color"}}
    sample_sets_table = pn.widgets.Tabulator(
        sample_sets_df,
        layout="fit_columns",
        selectable=True,
        pagination="remote",
        page_size=10,
        editors=sample_editors,
        formatters=sample_formatters,
    )
    return sample_sets_table


def make_individuals_table(df, sample_sets_df):
    ind_editors = {}
    for col in df.columns:
        ind_editors[col] = None
    ind_editors["sample_set_id"] = {
        "type": "list",
        "values": sample_sets_df.index.values.tolist(),
        "valuesLookup": True,
    }
    ind_editors["selected"] = {
        "type": "list",
        "values": [False, True],
        "valuesLookup": True,
    }
    ind_formatters = {"selected": {"type": "tickCross"}}

    individuals_table = pn.widgets.Tabulator(
        df,
        layout="fit_columns",
        selectable=True,
        pagination="remote",
        page_size=20,
        editors=ind_editors,
        formatters=ind_formatters,
        text_align={"selected": "center"},
    )

    return individuals_table


def sample_sets_md():
    return pn.pane.Markdown(
        """
        ## Sample sets

        You can change the name and color of each sample set. You can
        also add new sample set definitions which are inserted
        sequentially. In the individuals table, you can assign
        individuals to sample sets.

        """
    )


def individuals_md():
    return pn.pane.Markdown(
        """
        ## Individuals

        In the individuals table, you can assign
        individuals to sample sets and toggle their selection
        status. 
        """
    )


def page(tsm):
    sample_sets_df = pd.DataFrame(tsm.sample_sets).set_index(["id"])

    columns = [
        "name",
        "population",
        "sample_set_id",
        "selected",
        "longitude",
        "latitude",
    ]
    df = tsm.get_individuals(astype="df", deselected=True)[columns]

    sample_sets_table = make_sample_sets_table(sample_sets_df)

    def update_sample_set(event):
        if event.column == "color":
            tsm.sample_sets[event.row].color = event.value
        elif event.column == "name":
            tsm.sample_sets[event.row].name = event.value

    sample_sets_table.on_edit(update_sample_set)

    def update_individual(event):
        if event.column == "selected":
            tsm.toggle_individual(event.row)
        elif event.column == "sample_set_id":
            tsm.update_individual_sample_set(event.row, event.value)

    individuals_table = make_individuals_table(df, sample_sets_df)
    individuals_table.on_edit(update_individual)

    return pn.Column(
        sample_sets_md(),
        sample_sets_table,
        individuals_md(),
        individuals_table,
    )
