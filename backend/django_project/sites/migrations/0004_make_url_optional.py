from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("sites", "0003_add_phone_to_telegramaccount"),
    ]

    operations = [
        migrations.AlterField(
            model_name="site",
            name="url",
            field=models.URLField(unique=True, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="sitelink",
            name="url",
            field=models.URLField(unique=True, blank=True, null=True),
        ),
    ]

