from traits.api import HasTraits, List, Any, Instance
from traitsui.api import View, Item, VGroup, ListEditor


class TabbedPanelCollection(HasTraits):
    """Collect a list of HasTraits instances and display each
    of them as a tab in a tabbed notebook using ListEditor
    """

    # List of Traits object to be displayed in the notebook
    panels = List

    # The Traits object currently selected
    selected_panel = Instance(HasTraits)

    @classmethod
    def create(cls, **kwargs):
        """Create a TabbedPanelCollection containing the given
        HasTraits instances.

        Arguments
        ---------
        **kwargs :
            The values are the HasTraits instances to be collected.
            The keys in the keyword arguments are used to define
            attributes of the TabbedPanelCollection
            so that the HasTraits instances can be retrieved easily.

            As with any keyword arguments, the order of the keys
            is lost.

        Raises
        ------
        AttributeError
            If the given key is a pre-defined attribute/method

        Examples
        --------
        >>> all_panels = TabbedPanelCollection(panel_a=PanelA(),
                                               panel_b=PanelB())
        >>> all_panels.panel_a
        <PanelA at 0x7fdc974febd0>

        >>> all_panels.configure_traits()  # should display a notebook
        """

        instance = cls()

        for key, panel in kwargs.items():
            if hasattr(instance, key):
                message = "'{}' is a predefined attribute"
                raise AttributeError(message.format(key))
            setattr(instance, key, panel)

        instance.panels = kwargs.values()
        return instance

    def __iter__(self):
        return iter(self.panels)

    traits_view = View(
        VGroup(
            Item("panels",
                 show_label=False,
                 style="custom",
                 editor=ListEditor(use_notebook=True,
                                   selected="selected_panel",
                                   page_name=".label"))),
        dock="horizontal")


if __name__ == "__main__":
    from traits.api import Str, Instance

    class A(HasTraits):
        text = Str("hello")

    class B(HasTraits):
        text = Str("Bye")
        text2 = Str("Bye again")
        label = "B Panel"

    class C(HasTraits):
        items = Instance(TabbedPanelCollection)

        view = View(Item("items", style="custom"))

        def _items_default(self):
            return TabbedPanelCollection.create(a=A(), b=B())

    c = C()
    c.configure_traits()

    d = TabbedPanelCollection.create(a=A(), b=B())
    d.configure_traits(view="traits_view")

    d.a.configure_traits()
