from .layer import Layer


class LightLayer(Layer):
    def __init__(self, light_type, *args, **kwargs):
        """
        This class is not used at the moment.
        The LightLayer object represents a light layer within a composition.
        Args:
            light_type (Aep.LightType): The type of light.
        """
        super(Layer, self).__init__(*args, **kwargs)
        self.light_type = light_type
