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


def make_new_sample_set_button():
    create_button = pn.widgets.Button(
        name="➕ Create new sample set",
        button_type="primary",
    )
    return create_button


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

        The name and color of each sample set are editable. In the
        individuals table, you can assign individuals to sample set
        ids.

        """
    )


def individuals_md():
    return pn.pane.Markdown(
        """
        ## Individuals

        Assign individuals to sample sets and toggle their selection
        status for analyses and plots.
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

    new_sample_set_name = pn.widgets.TextInput(
        name="New sample set name",
        placeholder="Enter a string here...",
        max_length=128,
    )
    # TODO: alert is not responsive
    alert = pn.pane.Alert("", alert_type="success", visible=False)

    def create_new_sample_set(event):
        name = new_sample_set_name.value
        if name is not None and name != "":
            newid = tsm.create_sample_set(name)
            alert.object = f"Successfully created sample set {newid}:{name}"
            alert.visible = True

    create_button = make_new_sample_set_button()
    create_button.on_click(create_new_sample_set)

    return pn.Column(
        sample_sets_md(),
        new_sample_set_name,
        create_button,
        sample_sets_table,
        individuals_md(),
        individuals_table,
    )
