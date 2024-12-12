"""Overview page.

This file contains the class for the application's overview
page. The page includes both the main content with the information
about the data file given to the application as well as a sidebar
with a short description of the application.

"""

import panel as pn

from .core import View


class OverviewPage(View):
    """
    Represents the overview page of the tseda application.

    Attributes:
        key (str): A unique identifier for this view within the application.
        title (str): The title displayed on the page.

    Methods:
        __panel__() -> pn.Column: Defines the layout of the main content area.
        sidebar() -> pn.Column: Defines the layout of the sidebar content area.
    """

    key = "overview"
    title = "Overview"

    def __panel__(self) -> pn.Column:
        """
        Returns the main content of the page which is retrieved from the
        `datastore.tsm.ts` attribute.

        Returns:
            pn.Column: The layout for the main content area.
        """
        return pn.Column(pn.pane.HTML(self.datastore.tsm.ts))

    def sidebar(self) -> pn.Column:
        """
        Returns the content of the sidebar.

        Returns:
            pn.Column: The layout for the sidebar.
        """
        return pn.Column(
            pn.pane.HTML(
                "<h2 style='margin: 0;'>Overview</h2>",
                sizing_mode="stretch_width",
            ),
            pn.pane.Markdown(
                (
                    "Welcome to **tseda**! This is a tool that "
                    "you can use to analyze your tskit data file."
                ),
                sizing_mode="stretch_width",
            ),
        )
