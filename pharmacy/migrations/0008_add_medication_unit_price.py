from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0007_add_batch_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='medication',
            name='unit_price',
            field=models.DecimalField(
                max_digits=10,
                decimal_places=2,
                default=0.00,  # Setting a default value for existing records
            ),
            preserve_default=False,  # This will remove the default after migration
        ),
    ]