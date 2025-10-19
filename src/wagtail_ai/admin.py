from wagtail.admin.panels import FieldPanel
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from wagtail_ai.models import Prompt

@modeladmin_register
class PromptAdmin(ModelAdmin):
    model = Prompt
    menu_label = 'AI Prompts'
    menu_icon = 'code'
    list_display = ('label', 'feature', 'method', 'description')
    list_filter = ('feature', 'method')
    search_fields = ('label', 'description', 'prompt')

    panels = [
        FieldPanel('label'),
        FieldPanel('description'),
        FieldPanel('feature'),
        FieldPanel('method'),
        FieldPanel('prompt'),
    ]
