from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0008_add_medication_unit_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='medication',
            name='unit_of_measure',
            field=models.CharField(
                max_length=50,
                default='units',  # Setting a default value for existing records
            ),
            preserve_default=False,  # This will remove the default after migration
        ),
    ]