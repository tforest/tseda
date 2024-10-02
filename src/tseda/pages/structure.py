import panel as pn

wip = pn.pane.Alert("## WIP\nThis page is currently a placeholder!")
md = pn.pane.Markdown(
    """
    ## GNN Heatmap plots

    - GNN Heatmap (Z-score plot clustered by row)
    - Fst plot
    - PCA plot
    """
)


class StructurePage:
    key = "structure"
    title = "Structure"

    def __init__(self, tsm):
        self.tsm = tsm
        self.content = pn.Column(wip, md)
        self.sidebar = pn.Column(pn.pane.Markdown("# Structure"))
