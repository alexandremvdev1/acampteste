import os
import datetime
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse, JsonResponse, FileResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError
from django.db.models import Q, Sum
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import MercadoPagoConfig
from .forms import MercadoPagoConfigForm
import mercadopago
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Inscricao
import logging
from django.views.decorators.csrf import csrf_exempt

from .forms import (
    ContatoForm,
    DadosSaudeForm,
    PastoralMovimentoForm,
    VideoEventoForm,
    AlterarCredenciaisForm,
    PoliticaPrivacidadeForm,
    ParoquiaForm,
    UserAdminParoquiaForm,
    ParticipanteInicialForm,
    ParticipanteEnderecoForm,
    InscricaoSeniorForm,
    InscricaoJuvenilForm,
    InscricaoMirimForm,
    InscricaoServosForm,
    EventoForm,
    ConjugeForm
)

from .models import (
    PastoralMovimento,
    VideoEventoAcampamento,
    CrachaTemplate,
    Paroquia,
    EventoAcampamento,
    Inscricao,
    InscricaoSenior,    
    InscricaoJuvenil,
    InscricaoMirim,     
    InscricaoServos,     
    Conjuge,
    User,
    Pagamento,
    Participante,
    PoliticaPrivacidade,
    Contato
)


@login_required
def home_redirect(request):
    user = request.user
    if hasattr(user, 'is_admin_geral') and user.is_admin_geral():
        return redirect('inscricoes:admin_geral_dashboard')
    elif hasattr(user, 'is_admin_paroquia') and user.is_admin_paroquia():
        return redirect('inscricoes:admin_paroquia_painel')
    else:
        return redirect('inscricoes:login')

@login_required
def admin_geral_home(request):
    return HttpResponse("Bem-vindo, Administrador Geral!")

@login_required
def admin_paroquia_home(request):
    # Supondo que o usuário tenha atributo 'paroquia' diretamente ou via perfil
    paroquia = getattr(request.user, 'paroquia', None)
    nome_paroquia = paroquia.nome if paroquia else 'Sem Paróquia'
    return HttpResponse(f"Bem-vindo, Admin da Paróquia: {nome_paroquia}")

def is_admin_geral(user):
    return user.is_authenticated and user.is_admin_geral()

@login_required
@user_passes_test(is_admin_geral)
def admin_geral_dashboard(request):
    total_paroquias = Paroquia.objects.count()
    total_eventos = EventoAcampamento.objects.count()
    total_inscricoes = Inscricao.objects.count()
    total_inscricoes_confirmadas = Inscricao.objects.filter(pagamento_confirmado=True).count()
    total_usuarios = User.objects.filter(tipo_usuario='admin_paroquia').count()

    ultimas_paroquias = Paroquia.objects.order_by('-id')[:5]
    proximos_eventos = EventoAcampamento.objects.filter(data_inicio__gte=datetime.date.today()).order_by('data_inicio')[:5]
    inscricoes_recentes = Inscricao.objects.order_by('-data_inscricao')[:5]

    context = {
        'total_paroquias': total_paroquias,
        'total_eventos': total_eventos,
        'total_inscricoes': total_inscricoes,
        'total_inscricoes_confirmadas': total_inscricoes_confirmadas,
        'total_usuarios': total_usuarios,
        'ultimas_paroquias': ultimas_paroquias,
        'proximos_eventos': proximos_eventos,
        'inscricoes_recentes': inscricoes_recentes,
    }
    return render(request, 'inscricoes/admin_geral_dashboard.html', context)


def is_admin_geral(user):
    return user.is_authenticated and user.is_admin_geral()

@login_required
@user_passes_test(is_admin_geral)
def admin_geral_list_paroquias(request):
    paroquias = Paroquia.objects.all()
    return render(request, 'inscricoes/admin_geral_list_paroquias.html', {'paroquias': paroquias})

@login_required
@user_passes_test(is_admin_geral)
def admin_geral_create_paroquia(request):
    if request.method == 'POST':
        form = ParoquiaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inscricoes:admin_geral_list_paroquias')
    else:
        form = ParoquiaForm()
    return render(request, 'inscricoes/admin_geral_form_paroquia.html', {'form': form})

@login_required
@user_passes_test(is_admin_geral)
def admin_geral_edit_paroquia(request, pk):
    paroquia = get_object_or_404(Paroquia, pk=pk)
    if request.method == 'POST':
        form = ParoquiaForm(request.POST, instance=paroquia)
        if form.is_valid():
            form.save()
            return redirect('inscricoes:admin_geral_list_paroquias')
    else:
        form = ParoquiaForm(instance=paroquia)
    return render(request, 'inscricoes/admin_geral_form_paroquia.html', {'form': form})

@login_required
@user_passes_test(is_admin_geral)
def admin_geral_delete_paroquia(request, pk):
    paroquia = get_object_or_404(Paroquia, pk=pk)
    if request.method == 'POST':
        paroquia.delete()
        return redirect('inscricoes:admin_geral_list_paroquias')
    return render(request, 'inscricoes/admin_geral_confirm_delete.html', {'obj': paroquia, 'tipo': 'Paróquia'})


# -------- Usuários Admin Paróquia --------

@login_required
@user_passes_test(is_admin_geral)
def admin_geral_list_usuarios(request):
    usuarios = User.objects.filter(tipo_usuario='admin_paroquia')
    return render(request, 'inscricoes/admin_geral_list_usuarios.html', {'usuarios': usuarios})

@login_required
@user_passes_test(is_admin_geral)
def admin_geral_create_usuario(request):
    if request.method == 'POST':
        form = UserAdminParoquiaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inscricoes:admin_geral_list_usuarios')
    else:
        form = UserAdminParoquiaForm()
    return render(request, 'inscricoes/admin_geral_form_usuario.html', {'form': form})

@login_required
@user_passes_test(is_admin_geral)
def admin_geral_edit_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk, tipo_usuario='admin_paroquia')
    if request.method == 'POST':
        form = UserAdminParoquiaForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('inscricoes:admin_geral_list_usuarios')
    else:
        form = UserAdminParoquiaForm(instance=usuario)
    return render(request, 'inscricoes/admin_geral_form_usuario.html', {'form': form})

@login_required
@user_passes_test(is_admin_geral)
def admin_geral_delete_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk, tipo_usuario='admin_paroquia')
    if request.method == 'POST':
        usuario.delete()
        return redirect('inscricoes:admin_geral_list_usuarios')
    return render(request, 'inscricoes/admin_geral_confirm_delete.html', {'obj': usuario, 'tipo': 'Usuário'})

@login_required
def admin_paroquia_painel(request, paroquia_id=None):
    user = request.user

    # Se for admin paroquial
    if user.is_admin_paroquia():
        if not user.paroquia:
            messages.error(request, "⚠️ Sua conta não está vinculada a uma paróquia.")
            return redirect('logout')
        paroquia = user.paroquia

    # Se for admin geral, acessando com ID explícito
    elif user.is_admin_geral():
        if not paroquia_id:
            messages.error(request, "⚠️ Paróquia não especificada.")
            return redirect('inscricoes:admin_geral_list_paroquias')
        paroquia = get_object_or_404(Paroquia, id=paroquia_id)

    else:
        messages.error(request, "⚠️ Você não tem permissão para acessar este painel.")
        return redirect('logout')

    eventos = EventoAcampamento.objects.filter(paroquia=paroquia)

    return render(request, 'inscricoes/admin_paroquia_painel.html', {
        'paroquia': paroquia,
        'eventos': eventos,
    })

@login_required
def evento_novo(request):
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            evento = form.save(commit=False)
            if hasattr(request.user, 'paroquia') and request.user.paroquia:
                evento.paroquia = request.user.paroquia
            elif not evento.paroquia:
                messages.error(request, 'Selecione uma paróquia para o evento.')
                return render(request, 'inscricoes/evento_form.html', {'form': form})

            evento.save()
            messages.success(request, 'Evento criado com sucesso!')
            return redirect('inscricoes:admin_paroquia_painel')
    else:
        form = EventoForm(user=request.user)

    return render(request, 'inscricoes/evento_form.html', {'form': form})


@login_required
def eventos_listar(request):
    # sua lógica
    pass

@login_required
def inscricoes_listar(request):
    # código para listar inscrições
    pass

@login_required
def evento_editar(request, pk):
    # código para editar evento
    pass

@login_required
def evento_deletar(request, pk):
    # código para deletar evento
    pass

@login_required
def evento_participantes(request, evento_id):
    evento = get_object_or_404(EventoAcampamento, id=evento_id)

    # Verifica se o usuário tem permissão para acessar
    if request.user.is_admin_paroquia():
        if request.user.paroquia != evento.paroquia:
            return HttpResponseForbidden("Acesso negado.")
    elif not request.user.is_admin_geral():
        return HttpResponseForbidden("Acesso negado.")

    participantes = Inscricao.objects.filter(evento=evento).select_related('participante')
    total_participantes = participantes.count()  # Contagem dos participantes

    if request.method == "POST":
        inscricao_id = request.POST.get('inscricao_id')
        foi_selecionado = 'foi_selecionado' in request.POST

        try:
            inscricao = participantes.get(id=inscricao_id)  # garante que seja do evento
        except Inscricao.DoesNotExist:
            return HttpResponse("Inscrição não encontrada", status=404)

        inscricao.foi_selecionado = foi_selecionado
        inscricao.save()
        return redirect('inscricoes:evento_participantes', evento_id=evento.id)

    context = {
        'evento': evento,
        'participantes': participantes,
        'valor_inscricao': evento.valor_inscricao,
        'total_participantes': total_participantes,  # Adiciona ao contexto
    }
    return render(request, 'inscricoes/evento_participantes.html', context)


def inscricao_evento_publico(request, slug):
    evento = get_object_or_404(EventoAcampamento, slug=slug)
    # Aqui você pode colocar lógica para mostrar o formulário de inscrição, dados do evento, etc.
    context = {
        'evento': evento,
    }
    return render(request, 'inscricoes/evento_publico.html', context)

from .models import PoliticaPrivacidade


def ver_inscricao(request, pk):
    inscricao = get_object_or_404(Inscricao, pk=pk)
    passos = [
        'Inscrição enviada',
        'Seleção do participante',
        'Pagamento confirmado',
        'Participação confirmada',
    ]

    if inscricao.inscricao_concluida:
        inscricao_status = 4
    elif inscricao.pagamento_confirmado:
        inscricao_status = 3
    elif inscricao.foi_selecionado:
        inscricao_status = 2
    else:
        inscricao_status = 1

    politica = PoliticaPrivacidade.objects.first()  # ou use get() se só houver uma

    return render(request, 'inscricoes/ver_inscricao.html', {
        'inscricao': inscricao,
        'passos': passos,
        'inscricao_status': inscricao_status,
        'evento': inscricao.evento,
        'politica': politica,
    })


from .forms import InscricaoForm
from .forms import ParticipanteForm
from django.forms import modelformset_factory

@login_required
def editar_inscricao(request, pk):
    inscricao = get_object_or_404(Inscricao, pk=pk)
    participante = inscricao.participante

    # Formulário por tipo de evento
    base_form_class = {
        'senior': InscricaoSeniorForm,
        'juvenil': InscricaoJuvenilForm,
        'mirim': InscricaoMirimForm,
        'servos': InscricaoServosForm,
    }.get(inscricao.evento.tipo)

    base_instance = None
    if base_form_class:
        base_model = base_form_class._meta.model
        base_instance = base_model.objects.filter(inscricao=inscricao).first()

    # Conjuge
    conjuge_instance = getattr(inscricao, 'conjuge', None)

    # Contatos
    ContatoFormSet = modelformset_factory(
    Contato,
    form=ContatoForm,
    fields='__all__',  # ou especifique os campos manualmente
    extra=0,
    can_delete=False
)

    contatos_queryset = Contato.objects.filter(inscricao=inscricao)

    # Pagamento
    pagamento_instance = Pagamento.objects.filter(inscricao=inscricao).first()

    if request.method == 'POST':
        inscricao_form = InscricaoForm(request.POST, instance=inscricao)
        participante_form = ParticipanteForm(request.POST, request.FILES, instance=participante)
        base_form = base_form_class(request.POST, instance=base_instance) if base_form_class else None
        conjuge_form = ConjugeForm(request.POST, instance=conjuge_instance) if conjuge_instance else None
        contato_forms = ContatoFormSet(request.POST, queryset=contatos_queryset)
        pagamento_form = PagamentoForm(request.POST, instance=pagamento_instance) if pagamento_instance else None

        if all([
            inscricao_form.is_valid(),
            participante_form.is_valid(),
            (base_form.is_valid() if base_form else True),
            (conjuge_form.is_valid() if conjuge_form else True),
            contato_forms.is_valid(),
            (pagamento_form.is_valid() if pagamento_form else True),
        ]):
            inscricao_form.save()
            participante_form.save()
            if base_form: base_form.save()
            if conjuge_form: conjuge_form.save()
            if pagamento_form: pagamento_form.save()
            for contato_form in contato_forms:
                contato_form.save()
            messages.success(request, "Inscrição atualizada com sucesso!")
            return redirect('inscricoes:ver_inscricao', pk=inscricao.pk)
    else:
        inscricao_form = InscricaoForm(instance=inscricao)
        participante_form = ParticipanteForm(instance=participante)
        base_form = base_form_class(instance=base_instance) if base_form_class else None
        conjuge_form = ConjugeForm(instance=conjuge_instance) if conjuge_instance else None
        contato_forms = ContatoFormSet(queryset=contatos_queryset)
        pagamento_form = PagamentoForm(instance=pagamento_instance) if pagamento_instance else None

    return render(request, 'inscricoes/editar_inscricao.html', {
        'inscricao': inscricao,
        'inscricao_form': inscricao_form,
        'participante_form': participante_form,
        'base_form': base_form,
        'conjuge_form': conjuge_form,
        'contato_forms': contato_forms,
        'pagamento_form': pagamento_form,
    })


@login_required
def deletar_inscricao(request, pk):
    inscricao = get_object_or_404(Inscricao, pk=pk)
    if request.method == 'POST':
        inscricao.delete()
        return redirect('inscricoes:admin_paroquia_painel')
    return render(request, 'inscricoes/confirma_delecao.html', {'obj': inscricao})

@login_required
def ficha_inscricao(request, pk):
    inscricao = get_object_or_404(Inscricao, pk=pk)
    evento = inscricao.evento

    # Determina qual modelo de inscrição base usar
    if evento.tipo == 'senior':
        inscricao_base = get_object_or_404(InscricaoSenior, inscricao=inscricao)
    elif evento.tipo == 'juvenil':
        inscricao_base = get_object_or_404(InscricaoJuvenil, inscricao=inscricao)
    elif evento.tipo == 'mirim':
        inscricao_base = get_object_or_404(InscricaoMirim, inscricao=inscricao)
    else:  # 'servos'
        inscricao_base = get_object_or_404(InscricaoServos, inscricao=inscricao)

    # Adiciona a data de nascimento ao contexto
    data_nascimento = inscricao_base.data_nascimento

    return render(request, 'inscricoes/ficha_inscricao.html', {
        'inscricao': inscricao,
        'inscricao_base': inscricao_base,  # Passa a instância do modelo base
        'data_nascimento': data_nascimento,  # Passa a data de nascimento
    })

@login_required
def imprimir_cracha(request, pk):
    inscricao = get_object_or_404(Inscricao, pk=pk)
    # Aqui você pode gerar PDF ou página para impressão do crachá
    return render(request, 'inscricoes/imprimir_cracha.html', {'inscricao': inscricao})

def incluir_pagamento(request, inscricao_id):
    inscricao = get_object_or_404(Inscricao, id=inscricao_id)
    metodo_choices = Pagamento.MetodoPagamento.choices
    valor_default = inscricao.evento.valor_inscricao
    metodo_selecionado = None

    if request.method == 'POST':
        valor = request.POST.get('valor')
        metodo = request.POST.get('metodo')
        comprovante = request.FILES.get('comprovante')  # captura arquivo enviado

        erros = []

        # Validação valor
        if not valor:
            erros.append('O valor é obrigatório.')
        else:
            try:
                valor_decimal = float(valor)
                if valor_decimal <= 0:
                    erros.append('O valor deve ser maior que zero.')
            except ValueError:
                erros.append('Valor inválido.')

        # Validação método
        if metodo not in [choice[0] for choice in metodo_choices]:
            erros.append('Método de pagamento inválido.')

        if erros:
            for erro in erros:
                messages.error(request, erro)
            metodo_selecionado = metodo  # para manter selecionado no form
        else:
            pagamento, created = Pagamento.objects.update_or_create(
                inscricao=inscricao,
                defaults={
                    'valor': valor_decimal,
                    'metodo': metodo,
                    'status': Pagamento.StatusPagamento.CONFIRMADO,
                    'data_pagamento': timezone.now(),
                }
            )
            # Se enviou comprovante, salva no campo (substitui se já tinha)
            if comprovante:
                pagamento.comprovante = comprovante
                pagamento.save()

            # Marca a inscrição como pagamento confirmado
            if not inscricao.pagamento_confirmado:
                inscricao.pagamento_confirmado = True
                inscricao.save()

            messages.success(request, 'Pagamento incluído com sucesso!')
            return redirect('inscricoes:evento_participantes', evento_id=inscricao.evento.id)

    else:
        # GET: tenta carregar pagamento existente para preencher formulário
        try:
            pagamento = Pagamento.objects.get(inscricao=inscricao)
            valor_default = pagamento.valor
            metodo_selecionado = pagamento.metodo
        except Pagamento.DoesNotExist:
            metodo_selecionado = None

    return render(request, 'inscricoes/incluir_pagamento.html', {
        'inscricao': inscricao,
        'metodo_choices': metodo_choices,
        'valor_default': valor_default,
        'metodo_selecionado': metodo_selecionado,
        # Passa o pagamento para mostrar comprovante atual, se quiser
        'pagamento': Pagamento.objects.filter(inscricao=inscricao).first(),
    })

def inscricao_inicial(request, slug):
    evento   = get_object_or_404(EventoAcampamento, slug=slug)
    politica = PoliticaPrivacidade.objects.first()
    hoje     = date.today()

    # —> Se hoje estiver fora do período de inscrições, exibe template de encerradas
    if hoje < evento.inicio_inscricoes or hoje > evento.fim_inscricoes:
        return render(request, 'inscricoes/inscricao_encerrada.html', {
            'evento': evento,
            'politica': politica
        })

    if 'participante_id' in request.session:
        # Usuário já preencheu o formulário inicial
        endereco_form = ParticipanteEnderecoForm(request.POST or None)
        if request.method == 'POST' and endereco_form.is_valid():
            participante = Participante.objects.get(id=request.session['participante_id'])
            participante.CEP      = endereco_form.cleaned_data['CEP']
            participante.endereco = endereco_form.cleaned_data['endereco']
            participante.numero   = endereco_form.cleaned_data['numero']
            participante.bairro   = endereco_form.cleaned_data['bairro']
            participante.cidade   = endereco_form.cleaned_data['cidade']
            participante.estado   = endereco_form.cleaned_data['estado']
            participante.save()

            del request.session['participante_id']

            inscricao = Inscricao.objects.get(participante=participante, evento=evento)
            return redirect('inscricoes:formulario_personalizado', inscricao_id=inscricao.id)

        return render(request, 'inscricoes/inscricao_inicial.html', {
            'endereco_form': endereco_form,
            'evento': evento,
            'politica': politica
        })

    else:
        # Exibir o formulário inicial
        inicial_form = ParticipanteInicialForm(request.POST or None)
        if request.method == 'POST' and inicial_form.is_valid():
            cpf = ''.join(filter(str.isdigit, inicial_form.cleaned_data['cpf']))
            participante, created = Participante.objects.get_or_create(
                cpf=cpf,
                defaults={
                    'nome': inicial_form.cleaned_data['nome'],
                    'email': inicial_form.cleaned_data['email'],
                    'telefone': inicial_form.cleaned_data['telefone']
                }
            )
            if not created:
                participante.nome     = inicial_form.cleaned_data['nome']
                participante.email    = inicial_form.cleaned_data['email']
                participante.telefone = inicial_form.cleaned_data['telefone']
                participante.save()

            request.session['participante_id'] = participante.id

            inscricao_existente = Inscricao.objects.filter(
                participante=participante,
                evento=evento
            ).first()

            if inscricao_existente:
                form_map = {
                    'senior':  'inscricaosenior',
                    'juvenil': 'inscricaojuvenil',
                    'mirim':   'inscricaomirim',
                    'servos':  'inscricaoservos',
                }
                rel_name = form_map.get(evento.tipo.lower())
                if rel_name and getattr(inscricao_existente, rel_name, None):
                    return redirect('inscricoes:ver_inscricao', pk=inscricao_existente.id)
                return redirect('inscricoes:formulario_personalizado', inscricao_id=inscricao_existente.id)

            try:
                inscricao = Inscricao.objects.create(
                    participante=participante,
                    evento=evento,
                    paroquia=evento.paroquia
                )
            except IntegrityError:
                inscricao = Inscricao.objects.get(participante=participante, evento=evento)
                return redirect('inscricoes:ver_inscricao', pk=inscricao.id)

            return redirect('inscricoes:inscricao_inicial', slug=evento.slug)

        return render(request, 'inscricoes/inscricao_inicial.html', {
            'form': inicial_form,
            'evento': evento,
            'politica': politica
        })
    
    
def buscar_participante_ajax(request):
    cpf = request.GET.get('cpf', '').replace('.', '').replace('-', '')
    evento_id = request.GET.get('evento_id')
    print(f"[AJAX] CPF recebido no servidor: {cpf}, evento_id: {evento_id}")

    try:
        participante = Participante.objects.get(cpf=cpf)

        # só considera inscrição se for neste mesmo evento
        inscricao = None
        if evento_id:
            inscricao = Inscricao.objects.filter(
                participante=participante,
                evento_id=evento_id
            ).first()

        if inscricao:
            return JsonResponse({
                'ja_inscrito': True,
                'inscricao_id': inscricao.id
            })

        # participa mas não neste evento, devolve dados para auto-preenchimento
        return JsonResponse({
            'ja_inscrito': False,
            'nome': participante.nome,
            'email': participante.email,
            'telefone': participante.telefone
        })

    except Participante.DoesNotExist:
        return JsonResponse({'ja_inscrito': False})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': 'Erro interno: ' + str(e)}, status=500)
    

def formulario_personalizado(request, inscricao_id):
    # Obtém a inscrição, evento e política de privacidade
    inscricao = get_object_or_404(Inscricao, id=inscricao_id)
    evento = inscricao.evento
    politica = PoliticaPrivacidade.objects.first()

    # Mapeia tipo de evento → (FormClass, atributo OneToOne na Inscricao)
    form_map = {
        'senior':  (InscricaoSeniorForm, 'inscricaosenior'),
        'juvenil': (InscricaoJuvenilForm, 'inscricaojuvenil'),
        'mirim':   (InscricaoMirimForm, 'inscricaomirim'),
        'servos':  (InscricaoServosForm, 'inscricaoservos'),
    }
    tipo = evento.tipo.lower()
    if tipo not in form_map:
        raise Http404("Tipo de evento inválido.")

    FormClass, rel_name = form_map[tipo]
    instancia = getattr(inscricao, rel_name, None)
    conj_inst = getattr(inscricao, 'conjuge', None)

    if request.method == 'POST':
        form       = FormClass(request.POST, request.FILES, instance=instancia)
        conj_form  = ConjugeForm(request.POST, instance=conj_inst)
        if form.is_valid() and conj_form.is_valid():
            # Salva dados do formulário principal
            obj = form.save(commit=False)
            obj.inscricao = inscricao
            obj.save()

            # Salva dados do Conjuge
            conj = conj_form.save(commit=False)
            conj.inscricao = inscricao
            conj.save()

            return redirect('inscricoes:formulario_contato', inscricao_id=inscricao.id)
    else:
        form      = FormClass(instance=instancia)
        conj_form = ConjugeForm(instance=conj_inst)

    # Campos que o JS vai mostrar/ocultar
    campos_condicionais = [
        'nome_conjuge',
        'casado_na_igreja',
        'conjuge_inscrito',
        'ja_e_campista',
    ]

    return render(request, 'inscricoes/formulario_personalizado.html', {
        'form':               form,
        'conj_form':          conj_form,
        'inscricao':          inscricao,
        'evento':             evento,
        'campos_condicionais':campos_condicionais,
        'politica':           politica,
    })


def formulario_contato(request, inscricao_id):
    # Recupera a inscrição com base no ID
    inscricao = get_object_or_404(Inscricao, id=inscricao_id)

    # Recupera o evento associado à inscrição
    evento = inscricao.evento

    # Recupera a política de privacidade
    politica = PoliticaPrivacidade.objects.first()

    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            # Processar os dados do formulário
            inscricao.responsavel_1_nome = form.cleaned_data['responsavel_1_nome']
            inscricao.responsavel_1_telefone = form.cleaned_data['responsavel_1_telefone']
            inscricao.responsavel_1_grau_parentesco = form.cleaned_data['responsavel_1_grau_parentesco']
            inscricao.responsavel_1_ja_e_campista = form.cleaned_data['responsavel_1_ja_e_campista']

            inscricao.responsavel_2_nome = form.cleaned_data['responsavel_2_nome']
            inscricao.responsavel_2_telefone = form.cleaned_data['responsavel_2_telefone']
            inscricao.responsavel_2_grau_parentesco = form.cleaned_data['responsavel_2_grau_parentesco']
            inscricao.responsavel_2_ja_e_campista = form.cleaned_data['responsavel_2_ja_e_campista']

            inscricao.contato_emergencia_nome = form.cleaned_data['contato_emergencia_nome']
            inscricao.contato_emergencia_telefone = form.cleaned_data['contato_emergencia_telefone']
            inscricao.contato_emergencia_grau_parentesco = form.cleaned_data['contato_emergencia_grau_parentesco']
            inscricao.contato_emergencia_ja_e_campista = form.cleaned_data['contato_emergencia_ja_e_campista']

            # Salvar a instância da inscrição
            inscricao.save()

            # Redireciona para o formulário de dados de saúde
            return redirect('inscricoes:formulario_saude', inscricao_id=inscricao.id)
    else:
        # Inicializa o formulário com os dados existentes da inscrição
        form = ContatoForm(initial={
            'responsavel_1_nome': inscricao.responsavel_1_nome,
            'responsavel_1_telefone': inscricao.responsavel_1_telefone,
            'responsavel_1_grau_parentesco': inscricao.responsavel_1_grau_parentesco,
            'responsavel_1_ja_e_campista': inscricao.responsavel_1_ja_e_campista,
            'responsavel_2_nome': inscricao.responsavel_2_nome,
            'responsavel_2_telefone': inscricao.responsavel_2_telefone,
            'responsavel_2_grau_parentesco': inscricao.responsavel_2_grau_parentesco,
            'responsavel_2_ja_e_campista': inscricao.responsavel_2_ja_e_campista,
            'contato_emergencia_nome': inscricao.contato_emergencia_nome,
            'contato_emergencia_telefone': inscricao.contato_emergencia_telefone,
            'contato_emergencia_grau_parentesco': inscricao.contato_emergencia_grau_parentesco,
            'contato_emergencia_ja_e_campista': inscricao.contato_emergencia_ja_e_campista,
        })

    return render(request, 'inscricoes/formulario_contato.html', {
        'form': form,
        'inscricao': inscricao,
        'evento': evento,
        'politica': politica,
    })

def formulario_saude(request, inscricao_id):
    inscricao = get_object_or_404(Inscricao, id=inscricao_id)
    evento = inscricao.evento
    participante = inscricao.participante
    politica = PoliticaPrivacidade.objects.first()

    # detecta modelo específico de formulário
    if evento.tipo == 'senior':
        base_inscricao = get_object_or_404(InscricaoSenior, inscricao=inscricao)
    elif evento.tipo == 'juvenil':
        base_inscricao = get_object_or_404(InscricaoJuvenil, inscricao=inscricao)
    elif evento.tipo == 'mirim':
        base_inscricao = get_object_or_404(InscricaoMirim, inscricao=inscricao)
    else:
        base_inscricao = get_object_or_404(InscricaoServos, inscricao=inscricao)

    if request.method == 'POST':
        form_saude = DadosSaudeForm(request.POST, request.FILES, instance=base_inscricao)

        if form_saude.is_valid():
            # salva dados de saúde específicos
            form_saude.save()

            # marca inscrição como enviada
            inscricao.inscricao_enviada = True
            inscricao.save(update_fields=['inscricao_enviada'])

            # atualiza foto do participante, se enviada
            if 'foto' in request.FILES:
                participante.foto = request.FILES['foto']
                participante.save(update_fields=['foto'])

            return redirect('inscricoes:ver_inscricao', pk=inscricao.id)
        else:
            print("Erros no form_saude:", form_saude.errors)

    else:
        form_saude = DadosSaudeForm(instance=base_inscricao)
        # injeta o campo foto para exibição, sem alterar a lógica de DadosSaudeForm
        form_part = ParticipanteForm(instance=participante)
        form_saude.fields['foto'] = form_part.fields['foto']
        form_saude.initial['foto'] = form_part.initial.get('foto')
        form_saude.fields['foto'].widget.attrs.update({'class': 'form-control'})

    return render(request, 'inscricoes/formulario_saude.html', {
        'form': form_saude,
        'inscricao': inscricao,
        'evento': evento,
        'politica': politica,
    })


def preencher_dados_contato(request, inscricao_id):
    inscricao = get_object_or_404(Inscricao, id=inscricao_id)
    participante = inscricao.participante  # Associe ao participante da inscrição

    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            contato = form.save(commit=False)
            contato.participante = participante  # Associa ao participante
            contato.save()

            # Redireciona para a etapa final (dados de saúde ou página de sucesso)
            return redirect('preencher_dados_saude', inscricao_id=inscricao.id)
    else:
        form = ContatoForm()

    return render(request, 'dados_contato.html', {'form': form, 'inscricao': inscricao})

def form_inscricao(request):
    if request.method == "POST":
        cpf = request.POST.get("cpf")
        participante, criado = Participante.objects.get_or_create(cpf=cpf)
        participante.nome = request.POST.get("nome")
        participante.email = request.POST.get("email")
        participante.telefone = request.POST.get("telefone")
        participante.finalizado = True
        participante.save()
        return redirect('inscricoes:inscricao_finalizada', pk=participante.inscricao.id)

    return render(request, "inscricao.html")

def inscricao_finalizada(request, pk):
    inscricao = get_object_or_404(Inscricao, id=pk)
    return render(request, 'inscricoes/inscricao_finalizada.html', {'inscricao': inscricao})


from django.shortcuts import render, get_object_or_404
from .models import EventoAcampamento, Inscricao

def relatorio_crachas(request, evento_id):
    evento = get_object_or_404(EventoAcampamento, id=evento_id)
    cidade_selecionada = request.GET.get('cidade', '')

    # 1) Só inscrições concluídas
    inscricoes = Inscricao.objects.filter(
        evento=evento,
        inscricao_concluida=True
    ).select_related(
        'participante',
        'paroquia',
        'inscricaosenior',
        'inscricaojuvenil',
        'inscricaomirim',
        'inscricaoservos'
    )

    # 2) Filtro por cidade do participante
    if cidade_selecionada:
        inscricoes = inscricoes.filter(participante__cidade=cidade_selecionada)

    # 3) Lista de cidades únicas para o dropdown
    cidades = inscricoes.values_list('participante__cidade', flat=True).distinct().order_by('participante__cidade')

    # 4) Template de crachá
    cracha_template = CrachaTemplate.objects.first()

    return render(request, 'inscricoes/relatorio_crachas.html', {
        'evento': evento,
        'inscricoes': inscricoes,
        'cidades': cidades,
        'cidade_selecionada': cidade_selecionada,
        'cracha_template': cracha_template,
    })

def relatorio_fichas_sorteio(request, evento_id):
    evento = get_object_or_404(EventoAcampamento, id=evento_id)
    cidade = request.GET.get("cidade")

    # só inscrições concluídas
    inscricoes = Inscricao.objects.filter(
        evento=evento,
        inscricao_concluida=True
    )

    # filtra por cidade da paroquia
    if cidade:
        inscricoes = inscricoes.filter(paroquia__cidade=cidade)

    # lista de cidades para o <select>
    cidades = inscricoes.values_list('paroquia__cidade', flat=True).distinct().order_by('paroquia__cidade')

    return render(request, 'inscricoes/relatorio_fichas_sorteio.html', {
        'evento': evento,
        'inscricoes': inscricoes,           # agora iteramos nas Inscricoes
        'cidades': cidades,
        'cidade_selecionada': cidade,
    })

@login_required
def relatorio_inscritos(request, evento_id):
    evento = get_object_or_404(EventoAcampamento, id=evento_id)
    cidade_filtro      = request.GET.get('cidade', '')
    status_filtro      = request.GET.get('status', '')
    selecionado_filtro = request.GET.get('selecionado', '')

    # 1) Buscar as inscrições para o evento
    inscricoes = Inscricao.objects.filter(evento=evento)

    # 2) Aplicar filtros de cidade, status e seleção
    if cidade_filtro:
        inscricoes = inscricoes.filter(participante__cidade=cidade_filtro)
    if status_filtro == 'concluida':
        inscricoes = inscricoes.filter(inscricao_concluida=True)
    elif status_filtro == 'pendente':
        inscricoes = inscricoes.filter(inscricao_concluida=False)
    if selecionado_filtro == 'sim':
        inscricoes = inscricoes.filter(foi_selecionado=True)
    elif selecionado_filtro == 'nao':
        inscricoes = inscricoes.filter(foi_selecionado=False)

    # 3) Extrair participantes distintos
    participantes = Participante.objects.filter(inscricao__in=inscricoes).distinct()

    # 4) Lista de cidades
    cidades = participantes.values_list('cidade', flat=True).distinct().order_by('cidade')

    # 5) Buscar de fato as inscrições (para carregamento de OneToOne)
    inscricoes_qs = inscricoes.select_related(
        'inscricaosenior', 'inscricaojuvenil', 'inscricaomirim', 'inscricaoservos'
    )

    # 6) Montar dict para lookup no template
    inscricoes_dict = { i.participante_id: i for i in inscricoes_qs }

    # 7) Contagem de camisas
    # chaves devem bater com o template (minúsculas)
    tamanhos = ['PP','P','M','G','GG','XG','XGG']
    quantidades_camisas = { t.lower(): 0 for t in tamanhos }

    for inscr in inscricoes_qs:
        # para cada tipo, tenta buscar o objeto relacionado
        for rel in ('inscricaosenior','inscricaojuvenil','inscricaomirim','inscricaoservos'):
            obj = getattr(inscr, rel, None)
            if obj:
                size = (obj.tamanho_camisa or '').upper()
                key = size.lower()
                if key in quantidades_camisas:
                    quantidades_camisas[key] += 1
                break  # não precisa verificar as outras relações

    return render(request, 'inscricoes/relatorio_inscritos.html', {
        'evento': evento,
        'participantes': participantes,
        'cidades': cidades,
        'inscricoes_dict': inscricoes_dict,
        'cidade_filtro': cidade_filtro,
        'status_filtro': status_filtro,
        'selecionado_filtro': selecionado_filtro,
        'quantidades_camisas': quantidades_camisas,
    })


# Relatório Financeiro
def relatorio_financeiro(request, evento_id):
    evento = get_object_or_404(evento, id=evento_id)
    participantes = Participante.objects.filter(inscricao__evento=evento)
    # Em versão futura, pode incluir valores pagos, totais, etc.
    return render(request, 'relatorios/relatorio_financeiro.html', {
        'evento': evento,
        'participantes': participantes
    })

def pagina_video_evento(request, slug):
    evento = get_object_or_404(EventoAcampamento, slug=slug)
    # o vídeo está em evento.video.arquivo, se existir
    video = getattr(evento, 'video', None)
    return render(request, 'inscricoes/video_evento.html', {
        'evento': evento,
        'video': video,
    })

def alterar_politica(request):
    politica = PoliticaPrivacidade.objects.first()  # Pega a primeira (e única) política
    if not politica:
        politica = PoliticaPrivacidade.objects.create() # Cria se não existir

    if request.method == 'POST':
        form = PoliticaPrivacidadeForm(request.POST, request.FILES, instance=politica)
        if form.is_valid():
            form.save()
            return redirect('inscricoes:admin_geral_dashboard')  # Redireciona para o dashboard após salvar
    else:
        form = PoliticaPrivacidadeForm(instance=politica)

    return render(request, 'inscricoes/alterar_politica.html', {'form': form})

def relatorio_financeiro(request, evento_id):
    """
    Gera um relatório financeiro detalhado para um evento específico.
    """
    evento = EventoAcampamento.objects.get(pk=evento_id)

    # Calcula o total arrecadado por método de pagamento
    total_pix = Pagamento.objects.filter(
        inscricao__evento=evento,
        status=Pagamento.StatusPagamento.CONFIRMADO,
        metodo=Pagamento.MetodoPagamento.PIX
    ).aggregate(total=Sum('valor'))['total'] or 0

    total_credito = Pagamento.objects.filter(
        inscricao__evento=evento,
        status=Pagamento.StatusPagamento.CONFIRMADO,
        metodo=Pagamento.MetodoPagamento.CREDITO
    ).aggregate(total=Sum('valor'))['total'] or 0

    total_debito = Pagamento.objects.filter(
        inscricao__evento=evento,
        status=Pagamento.StatusPagamento.CONFIRMADO,
        metodo=Pagamento.MetodoPagamento.DEBITO
    ).aggregate(total=Sum('valor'))['total'] or 0

    total_dinheiro = Pagamento.objects.filter(
        inscricao__evento=evento,
        status=Pagamento.StatusPagamento.CONFIRMADO,
        metodo=Pagamento.MetodoPagamento.DINHEIRO
    ).aggregate(total=Sum('valor'))['total'] or 0

    # Calcula o total arrecadado com pagamentos confirmados
    total_arrecadado = total_pix + total_credito + total_debito + total_dinheiro

    # Calcula o total esperado (valor das inscrições * número de inscritos)
    total_esperado = evento.valor_inscricao * Inscricao.objects.filter(evento=evento).count()

    # Calcula o total pendente
    total_pendente = total_esperado - total_arrecadado

    # Recupera os pagamentos confirmados para detalhamento
    pagamentos_confirmados = Pagamento.objects.filter(
        inscricao__evento=evento,
        status=Pagamento.StatusPagamento.CONFIRMADO
    )

    context = {
        'evento': evento,
        'total_arrecadado': total_arrecadado,
        'total_esperado': total_esperado,
        'total_pendente': total_pendente,
        'pagamentos_confirmados': pagamentos_confirmados,
        'total_pix': total_pix,
        'total_credito': total_credito,
        'total_debito': total_debito,
        'total_dinheiro': total_dinheiro,
    }

    return render(request, 'inscricoes/relatorio_financeiro.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def ver_logs_bruto(request):
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'usuarios.log')
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            linhas = f.readlines()[-200:]
    else:
        linhas = ["Arquivo de log não encontrado."]
    return render(request, 'logs/ver_logs.html', {'linhas': linhas})


@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def ver_logs_lista(request):
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'usuarios.log')
    eventos = []

    if os.path.exists(log_path):
        try:
            with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                linhas = f.readlines()[-200:]
                for linha in linhas:
                    if 'LOGIN:' in linha:
                        partes = linha.split('|')
                        horario = partes[0].strip()
                        usuario = partes[-1].split('LOGIN: ')[1].split('|')[0].strip()
                        ip = partes[-1].split('IP: ')[1].strip()
                        eventos.append({'tipo': 'login', 'usuario': usuario, 'ip': ip, 'hora': horario})
                    elif 'LOGOUT:' in linha:
                        partes = linha.split('|')
                        horario = partes[0].strip()
                        usuario = partes[-1].split('LOGOUT: ')[1].split('|')[0].strip()
                        ip = partes[-1].split('IP: ')[1].strip()
                        eventos.append({'tipo': 'logout', 'usuario': usuario, 'ip': ip, 'hora': horario})
                    elif 'acessou' in linha:
                        partes = linha.split('|')
                        horario = partes[0].strip()
                        if 'acessou' in partes[-1]:
                            user_info = partes[-1].strip().split()
                            usuario = user_info[1]
                            caminho = partes[-1].split('acessou')[1].strip()
                            eventos.append({'tipo': 'acesso', 'usuario': usuario, 'caminho': caminho, 'hora': horario})
        except Exception as e:
            eventos.append({'tipo': 'erro', 'mensagem': f'Erro ao ler o arquivo de log: {str(e)}'})
    else:
        eventos.append({'tipo': 'erro', 'mensagem': 'Arquivo de log não encontrado.'})

    return render(request, 'logs/ver_logs_lista.html', {'eventos': eventos})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def download_logs(request):
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'usuarios.log')
    if os.path.exists(log_path):
        return FileResponse(open(log_path, 'rb'), as_attachment=True, filename='usuarios.log')
    else:
        return HttpResponse("Arquivo de log não encontrado.", status=404)
    
def pagina_video_evento(request, slug):
    evento = get_object_or_404(EventoAcampamento, slug=slug)

    try:
        video = evento.video
    except VideoEventoAcampamento.DoesNotExist:
        video = None

    if request.method == 'POST':
        form = VideoEventoForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            novo_video = form.save(commit=False)
            novo_video.evento = evento
            novo_video.save()
            return redirect('inscricoes:evento_participantes', evento_id=evento.id)
    else:
        form = VideoEventoForm(instance=video)

    return render(request, 'inscricoes/video_evento.html', {
        'evento': evento,
        'form': form,
        'video': video,
    })


User = get_user_model()

def alterar_credenciais(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = AlterarCredenciaisForm(request.POST, instance=user)
        if form.is_valid():
            user.username = form.cleaned_data['username']
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Credenciais atualizadas com sucesso!')
            return redirect('login')
    else:
        form = AlterarCredenciaisForm(instance=user)

    return render(request, 'inscricoes/alterar_credenciais.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_admin_geral())
def cadastrar_pastoral_movimento(request):
    if request.method == 'POST':
        form = PastoralMovimentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Pastoral/Movimento cadastrado com sucesso!')
            return redirect('inscricoes:listar_pastorais_movimentos')
    else:
        form = PastoralMovimentoForm()
    return render(request, 'pastorais/cadastrar.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_admin_geral())
def listar_pastorais_movimentos(request):
    pastorais = PastoralMovimento.objects.all()
    return render(request, 'pastorais/listar.html', {'pastorais': pastorais})

from django.shortcuts import render, get_object_or_404
from .models import EventoAcampamento, Participante, Inscricao

def verificar_selecao(request, evento_id):
    evento = get_object_or_404(EventoAcampamento, id=evento_id)
    status = None
    participante = None

    cpf = request.GET.get('cpf', '').strip()
    if cpf:
        try:
            participante = Participante.objects.get(cpf=cpf)
            inscricao = Inscricao.objects.get(
                evento=evento,
                participante=participante
            )
            # True ou False
            status = inscricao.foi_selecionado
        except Participante.DoesNotExist:
            status = 'nao_encontrado'
        except Inscricao.DoesNotExist:
            status = 'sem_inscricao'

    return render(request, 'inscricoes/verificar_selecao.html', {
        'evento': evento,
        'status': status,
        'participante': participante,
        'cpf': cpf,
    })

def is_admin_paroquia(user):
    return hasattr(user, 'is_admin_paroquia') and user.is_admin_paroquia()

def is_admin_paroquia(user):
    return user.is_authenticated and hasattr(user, 'is_admin_paroquia') and user.is_admin_paroquia()

@login_required
@user_passes_test(is_admin_paroquia)
def mp_config(request):
    paroquia = request.user.paroquia
    config, _ = MercadoPagoConfig.objects.get_or_create(paroquia=paroquia)

    if request.method == 'POST':
        form = MercadoPagoConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuração do Mercado Pago salva com sucesso!')
            # Redireciona de volta ao painel da paróquia
            return redirect('inscricoes:admin_paroquia_painel')
    else:
        form = MercadoPagoConfigForm(instance=config)

    return render(request, 'inscricoes/mp_config.html', {
        'form': form,
        'paroquia': paroquia,
    })

def iniciar_pagamento(request, inscricao_id):
    inscricao = get_object_or_404(Inscricao, id=inscricao_id)

    # 1) pega config do Mercado Pago
    try:
        config = inscricao.paroquia.mp_config
    except MercadoPagoConfig.DoesNotExist:
        messages.error(request, 'Pagamento não configurado. Entre em contato com a organização.')
        return redirect('inscricoes:pagina_de_contato')

    if not (config.access_token and config.access_token.strip()):
        messages.error(request, 'Pagamento não configurado. Entre em contato com a organização.')
        return redirect('inscricoes:pagina_de_contato')

    sdk = mercadopago.SDK(config.access_token.strip())
    pref_data = {
        "items": [{
            "title": f"Inscrição {inscricao.evento.nome}",
            "quantity": 1,
            "unit_price": float(inscricao.evento.valor_inscricao),
        }],
        "payer": {"email": inscricao.participante.email},
        "back_urls": {
            "success": request.build_absolute_uri(inscricao.inscricao_url),
            "failure": request.build_absolute_uri(inscricao.inscricao_url),
            "pending": request.build_absolute_uri(inscricao.inscricao_url),
        },
        "auto_return": "approved",
        "external_reference": str(inscricao.id),  # Adicionado external_reference
    }

    mp_pref = sdk.preference().create(pref_data)
    resp = mp_pref.get('response', {})

    init_point = resp.get('init_point') or resp.get('sandbox_init_point')
    if not init_point:
        logging.error("MP preference sem init_point: %r", resp)
        messages.error(request, 'Erro ao iniciar pagamento. Tente novamente mais tarde.')
        return redirect(inscricao.inscricao_url)

    if not init_point.lower().startswith(('http://', 'https://')):
        init_point = 'https://' + init_point

    return redirect(init_point)


def pagina_de_contato(request):
    # Tente obter a primeira paróquia ativa do banco de dados
    paroquia = Paroquia.objects.filter(status='ativa').first()

    # Se não houver paróquia ativa, você pode criar uma mensagem de erro
    # ou usar dados padrão. Aqui, passaremos None para o template.
    context = {'paroquia': paroquia}

    return render(request, 'inscricoes/pagina_de_contato.html', context)


@require_POST
@csrf_exempt
def mp_webhook(request):
    try:
        logging.info("Webhook do Mercado Pago recebido!")
        data = json.loads(request.body)
        logging.info(f"Dados recebidos do webhook: {data}")

        payment_id = data['data']['id']
        logging.info(f"ID do pagamento: {payment_id}")

        # Obtenha a configuração do Mercado Pago
        config = MercadoPagoConfig.objects.first()  # Adapte para sua lógica
        if not config:
            logging.error("MercadoPagoConfig não encontrada.")
            return HttpResponse(status=500)

        mp = mercadopago.SDK(config.access_token)
        payment = mp.payment().get(payment_id)['response']
        logging.info(f"Dados do pagamento do Mercado Pago: {payment}")

        inscricao_id = payment.get('external_reference')
        if not inscricao_id:
            logging.error(f"external_reference não encontrado no pagamento {payment_id}")
            return HttpResponse(status=400)

        inscricao = get_object_or_404(Inscricao, id=inscricao_id)

        # Verifique se o pagamento já existe
        pagamento, created = Pagamento.objects.get_or_create(
            transacao_id=payment_id,
            defaults={
                'inscricao': inscricao,
                'metodo': payment.get('payment_method_id', Pagamento.MetodoPagamento.PIX),
                'valor': payment.get('transaction_amount', 0),
                'data_pagamento': parse_datetime(payment.get('date_approved')) if payment.get('date_approved') else None,
            }
        )

        # Atualize o status do pagamento com base na resposta do Mercado Pago
        status = payment.get('status')
        if status == 'approved':
            pagamento.status = Pagamento.StatusPagamento.CONFIRMADO
            inscricao.pagamento_confirmado = True
            inscricao.save(update_fields=['pagamento_confirmado'])
            logging.info(f"Pagamento {payment_id} confirmado!")
        elif status == 'pending':
            pagamento.status = Pagamento.StatusPagamento.PENDENTE
            logging.info(f"Pagamento {payment_id} pendente.")
        else:
            pagamento.status = Pagamento.StatusPagamento.CANCELADO
            logging.warning(f"Pagamento {payment_id} cancelado.")
        pagamento.save()

        logging.info(f"Webhook do Mercado Pago processado com sucesso para o pagamento {payment_id}")
        return HttpResponse(status=200)

    except Inscricao.DoesNotExist:
        logging.error(f"Inscrição não encontrada para o pagamento: {payment_id}")
        return HttpResponse(status=404)
    except Exception as e:
        logging.exception(f"Erro ao processar webhook do Mercado Pago: {e}")
        return HttpResponse(status=500)

@login_required
def imprimir_todas_fichas(request, evento_id):
    evento = get_object_or_404(EventoAcampamento, id=evento_id)
    inscricoes = Inscricao.objects.filter(
        evento=evento,
        pagamento_confirmado=True
    ).select_related(
        'participante',
        'inscricaosenior','inscricaojuvenil','inscricaomirim','inscricaoservos',
        'conjuge','paroquia'
    )
    return render(request, 'inscricoes/imprimir_todas_fichas.html', {
        'evento': evento,
        'inscricoes': inscricoes,
    })