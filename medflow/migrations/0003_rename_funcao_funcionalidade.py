# Generated by Django 5.0.14 on 2025-04-20 23:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("medflow", "0002_profespecequipamento"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Funcao",
            new_name="Funcionalidade",
        ),
    ]
