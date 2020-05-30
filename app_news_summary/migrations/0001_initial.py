# Generated by Django 3.0.6 on 2020-05-29 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CrawlNews',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('sub_title', models.CharField(blank=True, max_length=100)),
                ('content', models.TextField()),
                ('sub_content', models.TextField(blank=True)),
                ('date', models.DateField(blank=True)),
                ('url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='SummaryCrawl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('content', models.TextField()),
                ('date', models.DateField()),
                ('url', models.URLField()),
                ('topic', models.CharField(max_length=10)),
                ('jeiba', models.TextField()),
                ('summary1', models.TextField()),
            ],
        ),
    ]
