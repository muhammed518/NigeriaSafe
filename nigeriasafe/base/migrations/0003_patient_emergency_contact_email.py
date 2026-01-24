# Generated migration for emergency_contact_email field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_task_status_task_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='emergency_contact_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
