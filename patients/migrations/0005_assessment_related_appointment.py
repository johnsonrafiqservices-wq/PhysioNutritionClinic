# Generated migration to add appointment relationship to Assessment model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0001_initial'),
        ('patients', '0004_patient_is_visiting_patient_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='related_appointment',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='assessments',
                to='appointments.appointment'
            ),
        ),
    ]
