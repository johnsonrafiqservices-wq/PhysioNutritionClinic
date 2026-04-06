from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('pharmacy', '0005_add_batch_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='batch',
            name='last_quality_check',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]