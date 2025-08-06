import logging
import random
import secrets
import string
import re
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out

from .models import Paroquia, User

logger = logging.getLogger('django')

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    logger.info(f"LOGIN: {user.username} | IP: {get_client_ip(request)}")

@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    logger.info(f"LOGOUT: {user.username} | IP: {get_client_ip(request)}")


User = get_user_model()

def gerar_senha_aleatoria(tamanho=8):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(tamanho))

def gerar_username_unico(nome):
    base = re.sub(r'\W+', '', nome.lower().replace(" ", ""))[:10]  # remove caracteres especiais e limita a 10
    username = base
    contador = 1

    # Garante unicidade
    while User.objects.filter(username=username).exists():
        sufixo = str(contador)
        corte = 10 - len(sufixo)
        username = f"{base[:corte]}{sufixo}"
        contador += 1

    return username

@receiver(post_save, sender=Paroquia)
def criar_usuario_paroquia(sender, instance, created, **kwargs):
    if created:
        senha = gerar_senha_aleatoria()
        username = gerar_username_unico(instance.nome)

        user = User.objects.create_user(
            username=username,
            email=instance.email,
            password=senha,
            tipo_usuario='admin_paroquia',
            paroquia=instance
        )

        # link para alterar usuário e senha (view a ser implementada)
        link_alterar = f"{settings.SITE_DOMAIN}/conta/alterar/{user.pk}/"

        # Envio do e-mail com emojis
        send_mail(
            subject='📬 Seus dados de acesso ao sistema de inscrição',
            message=(
                f"Olá {instance.responsavel},\n\n"
                f"Sua paróquia {instance.nome} foi cadastrada com sucesso!\n\n"
                f"🔐 Usuário: {username}\n"
                f"🔑 Senha: {senha}\n\n"
                f"Você pode alterar seu nome de usuário e senha neste link:\n🔗 {link_alterar}\n\n"
                f"🙏 Que Deus abençoe seu trabalho!\n"
                f"👨‍💻 Equipe do Sistema de Inscrição"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=False,
        )
