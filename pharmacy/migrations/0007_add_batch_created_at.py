from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0006_add_batch_last_quality_check'),
    ]

    operations = [
        migrations.AddField(
            model_name='batch',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='batch',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]