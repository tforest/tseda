import pandas as pd
import panel as pn


def page(tsm):
    def get_selected_data(selected_ids=None):
        if selected_ids is not None:
            for ind in tsm.individuals:
                tsm.deactivate_individual(ind.id)
            for sid in selected_ids:
                tsm.activate_individual(sid)
        df = tsm.get_individuals(astype="df", inactive=True)
        return df[
            [
                "name",
                "population",
                "sample_set_id",
                "active",
                "longitude",
                "latitude",
            ]
        ]

    df = get_selected_data()
    sample_sets_df = pd.DataFrame(tsm.sample_sets).set_index(["id"])
    # TODO: Add a button to update the sample set membership
    # individuals_list = [ind.id for ind in tsm.get_individuals(inactive=True)]
    # multi_select = pn.widgets.MultiSelect(
    #     name="select individual ids",
    #     value=individuals_list,
    #     options=df.index.values.tolist(),
    # ).value
    # dynamic_table = pn.bind(get_selected_data, selected_ids=multi_select)

    return pn.Column(
        pn.pane.Markdown("### Sample Sets"),
        pn.pane.DataFrame(sample_sets_df),
        pn.pane.Markdown("### Individuals"),
        pn.pane.DataFrame(df),
    )
