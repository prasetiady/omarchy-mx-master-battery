"""A menu-only StatusNotifierItem with a small read-only D-Bus menu."""

from gi.repository import Gio, GLib


ITEM_PATH = "/StatusNotifierItem"
MENU_PATH = "/MenuBar"
ITEM_XML = """<node><interface name="org.kde.StatusNotifierItem">
<method name="Activate"><arg type="i" direction="in"/><arg type="i" direction="in"/></method>
<method name="SecondaryActivate"><arg type="i" direction="in"/><arg type="i" direction="in"/></method>
<method name="ContextMenu"><arg type="i" direction="in"/><arg type="i" direction="in"/></method>
<method name="Scroll"><arg type="i" direction="in"/><arg type="s" direction="in"/></method>
<property name="Category" type="s" access="read"/><property name="Id" type="s" access="read"/>
<property name="Title" type="s" access="read"/><property name="Status" type="s" access="read"/>
<property name="IconName" type="s" access="read"/><property name="ItemIsMenu" type="b" access="read"/>
<property name="Menu" type="o" access="read"/>
</interface></node>"""
MENU_XML = """<node><interface name="com.canonical.dbusmenu">
<method name="GetLayout"><arg type="i" direction="in"/><arg type="i" direction="in"/><arg type="as" direction="in"/><arg type="u" direction="out"/><arg type="(ia{sv}av)" direction="out"/></method>
<method name="GetGroupProperties"><arg type="ai" direction="in"/><arg type="as" direction="in"/><arg type="a(ia{sv})" direction="out"/></method>
<method name="GetProperty"><arg type="i" direction="in"/><arg type="s" direction="in"/><arg type="v" direction="out"/></method>
<method name="AboutToShow"><arg type="i" direction="in"/><arg type="b" direction="out"/></method>
<method name="Event"><arg type="i" direction="in"/><arg type="s" direction="in"/><arg type="v" direction="in"/><arg type="u" direction="in"/></method>
<property name="Version" type="u" access="read"/><property name="TextDirection" type="s" access="read"/>
<property name="Status" type="s" access="read"/><property name="IconThemePath" type="as" access="read"/>
<signal name="ItemsPropertiesUpdated"><arg type="a(ia{sv})"/><arg type="a(ias)"/></signal>
<signal name="LayoutUpdated"><arg type="u"/><arg type="i"/></signal>
</interface></node>"""


class StatusNotifier:
    def __init__(self):
        self.labels = {1: "MX Master 2S", 2: "Battery: Checking…", 3: "State: Checking…"}
        self.connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.connection.register_object(ITEM_PATH, Gio.DBusNodeInfo.new_for_xml(ITEM_XML).interfaces[0], self.item_call, self.item_property, None)
        self.connection.register_object(MENU_PATH, Gio.DBusNodeInfo.new_for_xml(MENU_XML).interfaces[0], self.menu_call, self.menu_property, None)
        self.watch = Gio.bus_watch_name_on_connection(self.connection, "org.kde.StatusNotifierWatcher", Gio.BusNameWatcherFlags.NONE, self.register, None)

    def register(self, connection, name, owner):
        connection.call(name, "/StatusNotifierWatcher", name, "RegisterStatusNotifierItem", GLib.Variant("(s)", (ITEM_PATH,)), None, Gio.DBusCallFlags.NONE, -1, None, None, None)

    def item_property(self, connection, sender, path, interface, name):
        properties = {"Category": ("s", "Hardware"), "Id": ("s", "mx-master-battery"), "Title": ("s", "MX Master 2S"), "Status": ("s", "Active"), "IconName": ("s", "input-mouse"), "ItemIsMenu": ("b", True), "Menu": ("o", MENU_PATH)}
        signature, value = properties[name]
        return GLib.Variant(signature, value)

    def item_call(self, connection, sender, path, interface, method, parameters, invocation):
        invocation.return_value(None)

    def menu_property(self, connection, sender, path, interface, name):
        signature, value = {"Version": ("u", 3), "TextDirection": ("s", "ltr"), "Status": ("s", "normal"), "IconThemePath": ("as", [])}[name]
        return GLib.Variant(signature, value)

    def properties(self, item):
        if item == 0:
            return {"children-display": GLib.Variant("s", "submenu")}
        return {"label": GLib.Variant("s", self.labels[item]), "enabled": GLib.Variant("b", True)}

    def menu_call(self, connection, sender, path, interface, method, parameters, invocation):
        args = parameters.unpack()
        if method == "GetLayout":
            parent, depth, names = args
            children = [GLib.Variant("(ia{sv}av)", (i, self.properties(i), [])) for i in self.labels] if parent == 0 and depth != 0 else []
            invocation.return_value(GLib.Variant("(u(ia{sv}av))", (1, (parent, self.properties(parent), children))))
        elif method == "GetGroupProperties":
            ids, names = args
            invocation.return_value(GLib.Variant("(a(ia{sv}))", ([(i, self.properties(i)) for i in ids if i in self.labels or i == 0],)))
        elif method == "GetProperty":
            invocation.return_value(GLib.Variant("(v)", (self.properties(args[0])[args[1]],)))
        elif method == "AboutToShow":
            invocation.return_value(GLib.Variant("(b)", (False,)))
        else:
            invocation.return_value(None)

    def set_battery(self, level, state):
        self.labels[2] = "Battery: " + level
        self.labels[3] = "State: " + state
        updated = [(i, {"label": GLib.Variant("s", self.labels[i])}) for i in (2, 3)]
        self.connection.emit_signal(None, MENU_PATH, "com.canonical.dbusmenu", "ItemsPropertiesUpdated", GLib.Variant("(a(ia{sv})a(ias))", (updated, [])))
