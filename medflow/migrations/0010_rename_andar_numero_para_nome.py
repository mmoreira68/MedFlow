from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('medflow', '0009_agendamentosala_data_agendamento'),
    ]

    operations = [
        migrations.RenameField(
            model_name='andar',
            old_name='numero',
            new_name='nome',
        ),
    ]
