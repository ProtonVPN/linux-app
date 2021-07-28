import gi
from math import pi
gi.require_version('Gtk', '3.0')
import cairo
from gi.repository import Gtk, Gdk
from ...patterns.factory import WidgetFactory


class ServerLoad(Gtk.Frame):
    """Server Load.

    Used to displays the load icon and circle which
    displays the server load.

    __pos_modifier should be used to move the icon and the circle
    in tandem, as it will maintain them always centered.
    Thus, __BASE_ARC__POSITION and __BASE_ICON_POSITION should not
    be changed.

    Since set_source_rgb() method only accepts values from 0-1,
    percentages of rgb values have to be used instead.
    """

    _green = (0.302, 0.6392, 0.3451)
    _yellow = (0.9176, 0.7843, 0.098)
    _red = (0.9255, 0.3451, 0.3451)
    _inactive = (0.5961, 0.6157, 0.6627)

    __BASE_ARC__POSITION = (4, 6)
    __BASE_ICON_POSITION = (2, 0)
    __pos_modifier = 10

    __ARC_SIZE = 10
    __INFO_ICON_SIZE = 12

    def __init__(self, server_load):
        super().__init__()
        self.server_load = int(server_load)
        self.set_border_width(0)
        # Size was manually configured
        self.set_size_request(26, 0)
        self.surface = None
        self.set_property("has-tooltip", True)
        self.set_tooltip_text("{}%".format(server_load))

        self.area = Gtk.DrawingArea()
        self.add(self.area)

        self.area.connect("draw", self.on_draw)
        self.area.connect('configure-event', self.on_configure)

    def init_surface(self, area):
        # Destroy previous buffer
        if self.surface is not None:
            self.surface.finish()
            self.surface = None

        # Create a new buffer
        self.surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, area.get_allocated_width(),
            area.get_allocated_height()
        )

    def redraw(self):
        self.init_surface(self.area)
        context = cairo.Context(self.surface)
        context.scale(self.surface.get_width(), self.surface.get_height())
        self.do_drawing(context)
        self.surface.flush()

    def on_configure(self, area, event, data=None):
        self.redraw()
        return False

    def on_draw(self, area, context):
        if self.surface is not None:
            context.set_source_surface(self.surface, 0.0, 0.0)
            self.draw_radial_gradient_rect(context)
        return False

    def do_drawing(self, ctx):
        self.draw_radial_gradient_rect(ctx)

    def draw_radial_gradient_rect(self, ctx):
        self.create_info_icon(ctx)
        self.set_colour_according_to_load_value(ctx)
        self.create_load_circle(ctx)

    def create_info_icon(self, ctx):
        dummy = WidgetFactory.image("dummy")
        info_pixbuf = dummy.create_icon_pixbuf_from_name(
            "info-icon.svg",
            width=self.__INFO_ICON_SIZE, height=self.__INFO_ICON_SIZE
        )

        Gdk.cairo_set_source_pixbuf(
            ctx, info_pixbuf,
            self.__BASE_ICON_POSITION[0] + self.__pos_modifier,
            self.__BASE_ICON_POSITION[1] + self.__pos_modifier
        )
        ctx.paint()

    def set_colour_according_to_load_value(self, ctx):
        ctx.set_source_rgb(*self._green)
        if self.server_load > 75 and self.server_load < 91:
            ctx.set_source_rgb(*self._yellow)
        elif self.server_load > 90:
            ctx.set_source_rgb(*self._red)
        elif self.server_load == 0:
            ctx.set_source_rgb(*self._inactive)

    def create_load_circle(self, ctx):
        # y_pos, x_pos, radius, start_angle, stop_angle
        ctx.arc(
            self.__BASE_ARC__POSITION[0] + self.__pos_modifier,
            self.__BASE_ARC__POSITION[1] + self.__pos_modifier,
            self.__ARC_SIZE,
            0,
            2 * pi
        )
        ctx.stroke()
