from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('pharmacy', '0003_auto_20251012_2046'),
    ]

    operations = [
        migrations.AddField(
            model_name='batch',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('quarantine', 'Quarantine'), ('expired', 'Expired')], default='active', max_length=20),
        ),
    ]