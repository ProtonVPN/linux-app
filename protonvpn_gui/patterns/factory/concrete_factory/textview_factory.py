import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Pango
from ..abstract_widget_factory import WidgetFactory


class TextViewFactory(WidgetFactory):
    """Concrete Button Factory class.
    A textview can be used instead of a label where
    there is multiple lines to displays or edit.
    """

    concrete_factory = "textview"

    def __init__(self, text):
        self.__textbuffer = Gtk.TextBuffer()
        self.__textbuffer.set_text(text)
        self.__widget = Gtk.TextView(buffer=self.__textbuffer)
        self.__widget_context = self.__widget.get_style_context()

    @classmethod
    def factory(cls, widget_name, text):
        subclasses_dict = cls._get_subclasses_dict("textview")
        return subclasses_dict[widget_name](text)

    def __create_hyperlink_tag(self):
        # What can be applied to tags:
        # Background colour (“background” property)
        # Foreground colour (“foreground” property)
        # Underline (“underline” property)
        # Bold (“weight” property)
        # Italics (“style” property)
        # Strikethrough (“strikethrough” property)
        # Justification (“justification” property)
        # Size (“size” and “size-points” properties)
        # Text wrapping (“wrap-mode” property)
        #
        # To ensure the list is correct, check the following link::
        # https://python-gtk-3-tutorial.readthedocs.io/en/latest/textview.html#tags
        return self.__textbuffer.create_tag(
            underline=Pango.Underline.SINGLE,
            foreground="#9880FF"
        )

    @property
    def widget(self):
        """Get widget object."""
        return self.__widget

    @property
    def context(self):
        return self.__widget_context

    @property
    def text(self):
        """Get widget text."""
        return self.__textbuffer.get_text(
            self.__textbuffer.get_start_iter(),
            self.__textbuffer.get_end_iter(),
            self.__textbuffer
        )

    @text.setter
    def text(self, newvalue):
        """Set widget text.

        Args:
            newvalue (string)
        """
        self.__textbuffer.set_text(newvalue)

    def inset_text_at_end(self, text):
        end_iter = self.__textbuffer.get_end_iter()
        self.__textbuffer.insert(end_iter, text)

    def insert_link_at_end(self, text, url, callback=None):
        end_iter = self.__textbuffer.get_end_iter()
        _hyperlink_tag = self.__create_hyperlink_tag()
        if callback:
            _hyperlink_tag.connect("event", callback, url)
        self.__textbuffer.insert_with_tags(end_iter, text, _hyperlink_tag)

    @property
    def image(self):
        """Get widget image.

        This property replaces the label property.
        """
        return self.__widget.props.image

    @image.setter
    def image(self, newvalue):
        """Set widget image.

        This property replaces the label property.
        """
        self.__widget.props.image = newvalue

    @property
    def show(self):
        """Get widget visibility."""
        return self.__widget.props.visible

    @show.setter
    def show(self, newvalue):
        """Set widget visibiltiy."""
        self.__widget.props.visible = newvalue

    @property
    def expand_h(self):
        """Get horizontal expand."""
        return self.__widget.get_hexpand()

    @expand_h.setter
    def expand_h(self, newvalue):
        """Set horizontal expand."""
        self.__widget.set_hexpand(newvalue)

    @property
    def expand_v(self):
        """Get vertical expand."""
        return self.__widget.get_vexpand()

    @expand_v.setter
    def expand_v(self, newvalue):
        """Set vertical expand."""
        self.__widget.set_vexpand(newvalue)

    @property
    def align_h(self):
        """Get horizontal align."""
        return self.__widget.get_halign()

    @align_h.setter
    def align_h(self, newvalue):
        """Set horizontal align."""
        self.__widget.set_halign(newvalue)

    @property
    def align_v(self):
        """Get vertical align."""
        return self.__widget.get_valign()

    @align_v.setter
    def align_v(self, newvalue):
        """Set vertical align."""
        self.__widget.set_valign(newvalue)

    @property
    def editable(self):
        """Get if text is editable."""
        return self.__widget.get_editable()

    @editable.setter
    def editable(self, newvalue):
        """Set if text is editable."""
        self.__widget.set_editable(newvalue)

    @property
    def cursor(self):
        """Get if cursor is visible."""
        return self.__widget.get_cursor_visible()

    @cursor.setter
    def cursor(self, newvalue):
        """Set if cursor is visible."""
        self.__widget.set_cursor_visible(newvalue)

    @property
    def overwrite(self):
        """Get if text is overwritable."""
        return self.__widget.get_overwrite()

    @overwrite.setter
    def overwrite(self, newvalue):
        """Set text is overwritable."""
        self.__widget.set_overwrite(newvalue)

    @property
    def wrap_mode(self):
        return self.__widget.get_wrap_mode()

    @wrap_mode.setter
    def wrap_mode(self, newvalue):
        wrap_dict = {
            "none": Gtk.WrapMode(0),
            "char": Gtk.WrapMode(1),
            "word": Gtk.WrapMode(2),
            "word_char": Gtk.WrapMode(3),
        }
        if newvalue not in wrap_dict:
            raise NotImplementedError("Wrap mode not supported")

        self.__widget.set_wrap_mode(wrap_dict[newvalue])

    @property
    def overwrite(self):
        """Get if text is overwritable."""
        return self.__widget.get_overwrite()

    @overwrite.setter
    def overwrite(self, newvalue):
        """Set text is overwritable."""
        return self.__widget.set_overwrite(newvalue)

    @property
    def ident_h(self):
        """Get line indentation."""
        return self.__widget.get_indent()

    @ident_h.setter
    def ident_h(self, newvalue):
        """Set line indentation."""
        return self.__widget.set_indent(newvalue)

    @property
    def justify(self):
        return self.__widget.get_justification()

    @justify.setter
    def justify(self, newvalue):
        justify_dict = {
            "left": Gtk.Justification(0),
            "right": Gtk.Justification(1),
            "center": Gtk.Justification(2),
            "fill": Gtk.Justification(3),
        }
        if newvalue not in justify_dict:
            raise NotImplementedError("Wrap mode not supported")

        self.__widget.set_justification(justify_dict[newvalue])

    @property
    def max_width(self):
        return self.__widget.props.width_request

    @max_width.setter
    def max_width(self, newvalue):
        self.__widget.props.width_request = newvalue

    @property
    def accept_tabs(self):
        return self.__widget.get_accepts_tab()

    @accept_tabs.setter
    def accept_tabs(self, newvalue):
        self.__widget.set_accepts_tab(newvalue)

    def add_class(self, css_class):
        """Add CSS class."""
        self.__widget_context.add_class(css_class)

    def remove_class(self, css_class):
        """Remove CSS class."""
        if self.has_class(css_class):
            self.__widget_context.remove_class(css_class)

    def remove_all_classes(self):
        css_list = self.__widget_context.list_classes()
        for css_class in css_list:
            self.__widget_context.remove_class(css_class)

    def replace_all_by(self, css_class):
        self.remove_all_classes()
        self.add_class(css_class)

    def replace_old_class_with_new_class(self, old_classes, new_classes):
        """Replaces old_classes with new_classes.

        Args:
            old_classes (str|list)
            new_classes (str|list)
        """
        def worker(css_class):
            if isinstance(css_class, list):
                for class_ in css_class:
                    self.remove_class(class_)
            elif isinstance(css_class, str):
                self.remove_class(css_class)
            else:
                raise TypeError(
                    "Unexpected type (list or str expected, but got {})".format( # noqa
                        type(css_class)
                    )
                )
        worker(old_classes)
        worker(new_classes)

    def has_class(self, css_class):
        """Check if has CSS class."""
        return True if self.__widget_context.has_class(css_class) else False

    def connect(self, *args, **kwargs):
        self.__widget.connect(*args, **kwargs)

    def custom_content(self, widget):
        self.__widget.add(widget)


class Dummy(TextViewFactory):
    textview = "dummy_textview"

    def __init__(self, text):
        super().__init__(text)


class QuickSettingDescription(TextViewFactory):
    textview = "default"

    def __init__(self, text):
        super().__init__(text)
        self.align_h = Gtk.Align.FILL
        self.align_v = Gtk.Align.START
        self.editable = False
        self.cursor = False
        self.overwrite = False
        self.accept_tabs = False
        self.show = True
        self.wrap_mode = "word"
        self.max_width = 320
        self.justify = "fill"
        self.add_class("default-text-view")


class NewBrandDescription(TextViewFactory):
    textview = "new-brand"

    def __init__(self, text):
        super().__init__(text)
        self.align_h = Gtk.Align.CENTER
        self.align_v = Gtk.Align.START
        self.editable = False
        self.cursor = False
        self.overwrite = False
        self.accept_tabs = False
        self.show = True
        self.wrap_mode = "word"
        self.max_width = 430
        self.justify = "center"
        self.add_class("default-text-view")
