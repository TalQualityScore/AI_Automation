# --- File: app/src/managers/state_manager.py ---

class StateManager:
    """Manages the application's data state (objects, layers, properties)."""
    def __init__(self):
        self.object_properties = {}
        self.layer_order = []

    def add_object(self, props):
        """Adds a new object to the state and returns its generated tag."""
        tag = f"item_{len(self.object_properties)}"
        props['tag'] = tag

        self.object_properties[tag] = props
        self.layer_order.insert(0, tag) # Add to the top of the layer stack
        return tag

    def delete_object(self, tag):
        """Removes an object from the state."""
        if tag in self.object_properties:
            del self.object_properties[tag]
        if tag in self.layer_order:
            self.layer_order.remove(tag)

    def get_properties(self, tag):
        """Gets the properties for a single object by its tag."""
        return self.object_properties.get(tag)

    # --- FIX ---
    # This function was missing. It allows other managers to safely
    # get the current order of layers.
    def get_layer_order(self):
        """Returns the current list of layer tags."""
        return self.layer_order

    def update_properties(self, tag, updates):
        """Updates the properties of a single object."""
        if tag in self.object_properties:
            self.object_properties[tag].update(updates)

    def move_layer(self, tag, direction):
        """Moves a layer up or down in the visual stack."""
        if tag not in self.layer_order:
            return
        idx = self.layer_order.index(tag)
        new_idx = idx - direction

        if 0 <= new_idx < len(self.layer_order):
            self.layer_order.pop(idx)
            self.layer_order.insert(new_idx, tag)