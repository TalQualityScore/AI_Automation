# --- File: app/src/managers/event_handler.py ---

class EventHandler:
    def __init__(self, app):
        self.app = app

    def on_canvas_click(self, event):
        # --- FIX: Use find_closest to reliably get the top-most item ---
        closest = self.app.canvas.find_closest(event.x, event.y)
        if not closest:
            self.app.canvas_manager.select_item(None)
            return

        tags = self.app.canvas.gettags(closest[0])
        clickable_tags = [t for t in tags if "item_" in t]

        if clickable_tags:
            tag = clickable_tags[0]
            self.app.canvas_manager.select_item(tag)
            self.app._drag_data.update({"x": event.x, "y": event.y})
            self.app.canvas.tag_bind(tag, "<B1-Motion>", self.on_drag)
        else:
            self.app.canvas_manager.select_item(None)

    def on_drag(self, event):
        tag = self.app.selected_item_tag
        if not (tag and self.app.img_w > 0 and self.app.img_h > 0):
            return

        dx = event.x - self.app._drag_data["x"]
        dy = event.y - self.app._drag_data["y"]

        for item_id in self.app.canvas.find_withtag(tag):
            self.app.canvas.move(item_id, dx, dy)
        if self.app.selection_box:
            self.app.canvas.move(self.app.selection_box, dx, dy)

        self.app._drag_data["x"] = event.x
        self.app._drag_data["y"] = event.y

        props = self.app.state_manager.get_properties(tag)
        if props:
            main_item = self.app.canvas.find_withtag(tag)
            if main_item:
                coords = self.app.canvas.coords(main_item[0])
                updates = {
                    'rel_x': (coords[0] - self.app.img_x) / self.app.img_w,
                    'rel_y': (coords[1] - self.app.img_y) / self.app.img_h
                }
                self.app.state_manager.update_properties(tag, updates)

    def on_layer_select(self, event):
        sel = self.app.layer_listbox.curselection()
        if not sel: return

        selected_index = sel[0]
        layer_order = self.app.state_manager.get_layer_order()

        if selected_index < len(layer_order):
            tag = layer_order[selected_index]
            self.app.canvas_manager.select_item(tag, from_listbox=True)
        else:
            self.app.layer_listbox.selection_clear(0, tk.END)
            self.app.canvas_manager.select_item(None)