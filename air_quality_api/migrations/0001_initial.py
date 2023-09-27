# Generated by Django 4.1.7 on 2023-03-19 20:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GraphData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='GraphValue',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('value', models.FloatField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('graph_data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='air_quality_api.graphdata')),
            ],
        ),
    ]
