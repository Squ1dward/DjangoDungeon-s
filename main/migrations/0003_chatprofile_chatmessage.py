# Generated by Django 5.1 on 2025-02-21 07:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_character_characterstats_characterweapon_enchantment_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatProfile',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('creationDate', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('message', models.TextField()),
                ('postDate', models.DateTimeField()),
                ('userId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('profileId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.chatprofile')),
            ],
        ),
    ]
