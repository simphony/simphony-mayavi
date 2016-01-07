from traits.api import HasTraits, List, Any
from traitsui.api import View, Item, VGroup, ListEditor


class TabbedPanelCollection(HasTraits):

    panels = List
    selected_panel = Any

    def __init__(self, **kwargs):
        for key, panel in kwargs.items():
            if hasattr(self, key):
                message = "'{}' is a predefined attribute"
                raise AttributeError(message.format(key))
            setattr(self, key, panel)

        self.panels = kwargs.values()

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

        def __init__(self):
            self.items = TabbedPanelCollection(a=A(), b=B())

    c = C()
    c.configure_traits()

    d = TabbedPanelCollection(a=A(), b=B())
    d.configure_traits(view="traits_view")

    d.a.configure_traits()
