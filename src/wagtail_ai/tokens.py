class NoTokenLimitFound(Exception):
    pass


def get_default_token_limit(model_id: str) -> int:
    """
    Get token limits for known models.
    """

    # TODO: Add ability to register more default models, e.g. in Django settings.

    match model_id:
        case "gpt-3.5-turbo":
            return 4096
        case "gpt-3.5-turbo-16k":
            return 16385
        case "gpt-4":
            return 8192
        case "gpt-4-32k":
            return 32768
        case _:
            raise NoTokenLimitFound(model_id)
