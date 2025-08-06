from django.apps import AppConfig

class InscricoesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inscricoes'

    def ready(self):
        import inscricoes.signals


class InscricoesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inscricoes'

    def ready(self):
        import inscricoes.signals
