import panel as pn


def page(tsm):
    return pn.pane.Markdown(
        """
        ## GNN Heatmap plots

        - GNN Heatmap (Z-score plot clustered by row)
        - Fst plot
        - PCA plot
        """
    )
