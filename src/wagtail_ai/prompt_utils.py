from wagtail_ai.models import Prompt, AgentPromptDefaults

def get_feature_prompt(feature_name: str) -> str:
    try:
        prompt = Prompt.objects.filter(feature=feature_name).first()
        if prompt:
            return prompt.prompt_value
    except Prompt.DoesNotExist:
        pass

    default_method = getattr(AgentPromptDefaults, f"{feature_name}_prompt")
    return default_method()
