# inscricoes/migrations/0003_participante_qr_token.py
from django.db import migrations, models
import uuid


def populate_qr_tokens(apps, schema_editor):
    Participante = apps.get_model('inscricoes', 'Participante')

    # set para evitar qualquer chance de colisão durante o populate
    usados = set(
        Participante.objects.exclude(qr_token__isnull=True).values_list('qr_token', flat=True)
    )

    for p in Participante.objects.all():
        if not p.qr_token:
            token = uuid.uuid4()
            while token in usados:
                token = uuid.uuid4()
            p.qr_token = token
            p.save(update_fields=['qr_token'])
            usados.add(token)


class Migration(migrations.Migration):

    dependencies = [
        ('inscricoes', '0002_inscricaojuvenil_alergia_alimento_and_more'),
    ]

    operations = [
        # 1) Adiciona o campo SEM unique, SEM default, e null=True
        migrations.AddField(
            model_name='participante',
            name='qr_token',
            field=models.UUIDField(editable=False, null=True, verbose_name='Token para QR Code'),
        ),

        # 2) Popula cada registro com um UUID único
        migrations.RunPython(populate_qr_tokens, migrations.RunPython.noop),

        # 3) Agora aplica unique=True e null=False
        migrations.AlterField(
            model_name='participante',
            name='qr_token',
            field=models.UUIDField(editable=False, unique=True, null=False, verbose_name='Token para QR Code'),
        ),
    ]
