import warnings


class WagtailAISettingsDeprecationWarning(DeprecationWarning):
    pass


warnings.filterwarnings("always", category=WagtailAISettingsDeprecationWarning)
