

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtail_ai', '0003_agentsettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='prompt',
            name='feature',
            field=models.CharField(blank=True, choices=[('page_title', 'Page title'), ('page_description', 'Page description'), ('image_title', 'Image title'), ('image_description', 'Image description'), ('contextual_alt_text', 'Contextual alt text')], help_text='Feature this prompt applies to.', max_length=50, null=True),
        ),
    ]
