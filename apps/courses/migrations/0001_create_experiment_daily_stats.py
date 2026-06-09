# -*- coding: utf-8 -*-
from django.db import migrations, models
import uuid


def generate_uuid_hex():
    return uuid.uuid4().hex[:32]


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TbExperimentDailyStats',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, default=generate_uuid_hex, serialize=False)),
                ('experiment_id', models.CharField(max_length=255)),
                ('stat_date', models.DateField()),
                ('visit_count', models.IntegerField(default=0)),
                ('practice_count', models.IntegerField(default=0)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'tb_experiment_daily_stats',
                'unique_together': {('experiment_id', 'stat_date')},
            },
        ),
    ]
