# Generated by Django 3.2.20 on 2023-12-11 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0003_dataset_submitted_as_prepared'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='generated_uid',
            field=models.CharField(max_length=128),
        ),
        migrations.AddConstraint(
            model_name='dataset',
            constraint=models.UniqueConstraint(condition=models.Q(('state', 'OPERATION')), fields=('generated_uid',), name='unique_operational_dataset_output_hash'),
        ),
    ]
