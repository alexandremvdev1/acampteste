from django.contrib import admin
from .models import CrachaTemplate
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import PoliticaPrivacidade
from .models import VideoEventoAcampamento
from .models import (
    Paroquia, Participante, EventoAcampamento, Inscricao, Pagamento,
    InscricaoSenior, InscricaoJuvenil, InscricaoMirim, InscricaoServos, User, PastoralMovimento, Contato, Conjuge, MercadoPagoConfig
)

@admin.register(Paroquia)
class ParoquiaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'estado', 'responsavel', 'email', 'telefone')
    search_fields = ('nome', 'cidade', 'responsavel')

@admin.register(Participante)
class ParticipanteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'telefone', 'email')
    search_fields = ('nome', 'cpf', 'email')

@admin.register(EventoAcampamento)
class EventoAcampamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'paroquia', 'data_inicio', 'data_fim', 'inicio_inscricoes', 'fim_inscricoes', 'slug')
    list_filter = ('tipo', 'paroquia')
    prepopulated_fields = {'slug': ('nome',)}
    search_fields = ('nome', 'paroquia__nome')

@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = (
        'participante', 'evento', 'paroquia', 'data_inscricao',
        'foi_selecionado', 'pagamento_confirmado', 'inscricao_concluida'
    )
    list_filter = ('evento', 'foi_selecionado', 'pagamento_confirmado', 'paroquia')
    search_fields = ('participante__nome', 'evento__nome', 'paroquia__nome')

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('inscricao', 'metodo', 'valor', 'status', 'data_pagamento', 'transacao_id')
    list_filter = ('status', 'metodo')
    search_fields = ('inscricao__participante__nome', 'transacao_id')

@admin.register(InscricaoSenior)
class InscricaoSeniorAdmin(admin.ModelAdmin):
    list_display = ('inscricao', 'data_nascimento', 'paroquia', 'batizado')  # Alterado 'igreja' para 'paroquia'
    search_fields = ('inscricao__participante__nome', 'paroquia')  # Alterado 'igreja' para 'paroquia'

@admin.register(InscricaoJuvenil)
class InscricaoJuvenilAdmin(admin.ModelAdmin):
    list_display = ('inscricao', 'data_nascimento', 'paroquia', 'batizado')  # Alterado 'igreja' para 'paroquia'
    search_fields = ('inscricao__participante__nome', 'paroquia')  # Alterado 'igreja' para 'paroquia'

@admin.register(InscricaoMirim)
class InscricaoMirimAdmin(admin.ModelAdmin):
    list_display = ('inscricao', 'data_nascimento', 'paroquia', 'batizado')  # Alterado 'igreja' para 'paroquia'
    search_fields = ('inscricao__participante__nome', 'paroquia')  # Alterado 'igreja' para 'paroquia'

@admin.register(InscricaoServos)
class InscricaoServosAdmin(admin.ModelAdmin):
    list_display = ('inscricao', 'data_nascimento', 'paroquia', 'batizado')  # Alterado 'igreja' para 'paroquia'
    search_fields = ('inscricao__participante__nome', 'paroquia')  # Alterado 'igreja' para 'paroquia'

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'tipo_usuario', 'paroquia', 'is_staff', 'is_active')
    list_filter = ('tipo_usuario', 'is_staff', 'is_active', 'paroquia')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('email', 'tipo_usuario', 'paroquia')}),
        ('Permissões', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Datas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    search_fields = ('username', 'email', 'tipo_usuario')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

@admin.register(PoliticaPrivacidade)
class PoliticaPrivacidadeAdmin(admin.ModelAdmin):
    list_display = ('__str__',)

@admin.register(VideoEventoAcampamento)
class VideoEventoAcampamentoAdmin(admin.ModelAdmin):
    list_display = ('evento', 'titulo', 'arquivo')

@admin.register(PastoralMovimento)
class PastoralMovimentoAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']


@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'grau_parentesco', 'ja_e_campista', 'inscricao')
    search_fields = ('nome', 'telefone', 'grau_parentesco', 'inscricao__participante__nome')
    list_filter = ('ja_e_campista',)

@admin.register(Conjuge)
class ConjugeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'inscricao', 'conjuge_inscrito', 'ja_e_campista')
    list_filter = ('conjuge_inscrito', 'ja_e_campista')
    search_fields = ('nome', 'inscricao__participante__nome', 'inscricao__participante__cpf')

    # Se quiser mostrar link para a inscrição
    def inscricao(self, obj):
        return obj.inscricao.participante.nome
    inscricao.short_description = 'Participante'

@admin.register(CrachaTemplate)
class CrachaTemplateAdmin(admin.ModelAdmin):
    list_display = ("nome",)

@admin.register(MercadoPagoConfig)
class MercadoPagoConfigAdmin(admin.ModelAdmin):
    list_display = ('paroquia', 'public_key', 'sandbox_mode')
    list_filter  = ('sandbox_mode',)
    search_fields = ('paroquia__nome',)