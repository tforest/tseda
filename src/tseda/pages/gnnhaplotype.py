import panel as pn

pn.extension()


def page(tsm):
    md = pn.pane.Markdown(
        """
        ## GNN haplotype plots

        
        """
    )

    sample_id = pn.widgets.TextInput(
        name="Enter sample ID",
        placeholder="Enter a string here...",
        max_length=128,
    )

    return pn.Column(md, sample_id)
