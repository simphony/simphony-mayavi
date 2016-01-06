from collections import namedtuple

from traits.api import HasTraits, Str, Instance
from traitsui.api import View, Group, Item


class TraitNamedTuple(HasTraits):

    def __init__(self, **kwargs):
        NamedTuple = namedtuple("NamedTuple", kwargs.keys())
        self.items = NamedTuple(**kwargs)
        self._keys = kwargs.keys()

    def default_traits_view(self):
        item_views = []

        # Collect all the View object
        for item in self.items:
            view = item.trait_view()
            item_views.append(view.content.content[0])

        # Display them as in tabs
        all_items = Group(*item_views, layout="tabbed")

        for inner_group, name in zip(all_items.content, self._keys):
            # modify the reference to the object
            inner_group.object = "object.{}".format(name)
            # if label is not defined in the trait view
            # use the attribute name
            if not inner_group.label:
                inner_group.label = name

        return View(all_items, resizable=True)

    def __getattr__(self, key):
        # get called when key is not found in the usual places
        return getattr(self.items, key)

    def __getitem__(self, key):
        return self.items[key]

    def __contains__(self, key):
        return key in self.items

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __reversed__(self):
        return reversed(self.items)

    def index(self, value):
        return self.items.index(value)

    def count(self, value):
        return self.items.count(value)


if __name__ == "__main__":
    class A(HasTraits):
        a = Str("hello")

    class B(HasTraits):
        b = Str("Bye")

    class C(HasTraits):
        items = Instance(TraitNamedTuple)

        view = View(Item("items", style="custom"))

        def __init__(self):
            self.items = TraitNamedTuple(a=A(), b=B())

    c = C()
    c.configure_traits()
