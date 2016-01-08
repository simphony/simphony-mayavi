from traits.api import HasTraits, List, Any
from traitsui.api import View, Item, VGroup, ListEditor


class TabbedPanelCollection(HasTraits):

    panels = List
    selected_panel = Any

    @classmethod
    def create(cls, **kwargs):
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
