# -*- coding: utf-8 -*-
import uuid
import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from django.db import models

from inscricoes.models import (
    Paroquia, PastoralMovimento, Participante, EventoAcampamento,
    Inscricao, InscricaoStatus, InscricaoCasais, Pagamento,
    PoliticaPrivacidade, PoliticaReembolso, VideoEventoAcampamento, CrachaTemplate,
    Grupo, Ministerio, AlocacaoGrupo, AlocacaoMinisterio
)

User = get_user_model()

# ----------------- Configs -----------------
CIDADES_TO = [
    "Palmas","Araguaína","Gurupi","Porto Nacional","Paraíso do Tocantins",
    "Colinas do Tocantins","Dianópolis","Guaraí","Miracema do Tocantins",
    "Tocantinópolis","Wanderlândia","Formoso do Araguaia","Pedro Afonso",
    "Caseara","Pium","Lagoa da Confusão","Araguatins","Augustinópolis",
    "Xambioá","Pequizeiro",
]

NOME_CASAIS = "EC São José 2025"
# o nome do servos será gerado automaticamente pelo post_save: "Servos – EC São José 2025"

# Catálogo fixo (nome → HEX) — deve casar com seu CORES_PADRAO
GRUPOS_FIXOS = [
    ("Amarelo",  "#F59E0B"),
    ("Vermelho", "#EF4444"),
    ("Azul",     "#3B82F6"),
    ("Verde",    "#10B981"),
]

MINISTERIOS_FIXOS = [
    "Liturgia","Música","Intercessão","Cozinha","Ambientação","Acolhida",
    "Secretaria","Comunicação","Fotografia","Transporte","Limpeza","Apoio",
    "Financeiro","Segurança","Crianças","Saúde/Enfermaria",
]

# ----------------- Helpers -----------------
def periodo(offset_dias=20, dur=3):
    di = date.today() + timedelta(days=offset_dias)
    df = di + timedelta(days=dur)
    inicio_ins = date.today() - timedelta(days=5)
    fim_ins = di - timedelta(days=1)
    return di, df, inicio_ins, fim_ins

def cpf_fake(i: int) -> str:
    return f"15{i:09d}"[:11]

def ensure_pagamento(ins, confirmado: bool, valor: Decimal):
    defaults = {
        "metodo": Pagamento.MetodoPagamento.PIX,
        "valor": valor,
        "status": Pagamento.StatusPagamento.CONFIRMADO if confirmado else Pagamento.StatusPagamento.PENDENTE,
        "data_pagamento": timezone.now() if confirmado else None,
        "transacao_id": f"TX-{uuid.uuid4().hex[:10]}",
        "fee_mp": Decimal("0.00"),
        "net_received": valor if confirmado else Decimal("0.00"),
    }
    pg, created = Pagamento.objects.get_or_create(inscricao=ins, defaults=defaults)
    if not created:
        changed = False
        for k, v in defaults.items():
            if getattr(pg, k) != v:
                setattr(pg, k, v); changed = True
        if changed:
            pg.save()

def fast_status(ins: Inscricao, target: str):
    enviada = target != InscricaoStatus.RASCUNHO
    sel = target in {InscricaoStatus.CONVOCADA, InscricaoStatus.PAG_PENDENTE, InscricaoStatus.PAG_CONFIRMADO}
    conf = target == InscricaoStatus.PAG_CONFIRMADO
    conc = conf
    Inscricao.objects.filter(pk=ins.pk).update(
        status=target,
        inscricao_enviada=enviada,
        foi_selecionado=sel,
        pagamento_confirmado=conf,
        inscricao_concluida=conc,
    )
    ins.status = target
    ins.inscricao_enviada = enviada
    ins.foi_selecionado = sel
    ins.pagamento_confirmado = conf
    ins.inscricao_concluida = conc

# ---------- nomes completos e únicos (realistas) ----------
FIRST_MALE = [
    "Alexandre","Carlos","João","Lucas","Rafael","Gustavo","Bruno","André","Marcelo","Thiago",
    "Paulo","Pedro","Felipe","Diego","Eduardo","Henrique","Leandro","Rodrigo","Roberto","Mateus",
    "Caio","Daniel","Murilo","Vitor","Fábio","Gabriel","Ícaro","Leonardo","Marcos","Rogério",
]
FIRST_FEMALE = [
    "Ana","Mariana","Fernanda","Juliana","Camila","Patrícia","Larissa","Renata","Aline","Roberta",
    "Carolina","Bianca","Beatriz","Bruna","Daniela","Elaine","Isabela","Letícia","Michele","Natália",
    "Paula","Priscila","Rafaela","Sabrina","Simone","Talita","Vanessa","Viviane","Yasmin","Kelly",
]
SOBRENOMES_A = [
    "da Silva","Silva","dos Santos","Santos","Oliveira","Souza","Pereira","Lima","Carvalho","Ribeiro",
    "Almeida","Gomes","Martins","Rocha","Barbosa","Araujo","Melo","Batista","Teixeira","Moreira",
    "Costa","Ferreira","Nunes","Correia","Pinto","Cardoso","Machado","Mendes","Neves","Santana",
]
SOBRENOMES_B = [
    "Vieira","Cavalcanti","Monteiro","Figueiredo","Cunha","Tavares","Azevedo","Rodrigues","Rezende","Pires",
    "Sales","Campos","Dias","Queiroz","Barros","Farias","Fonseca","Assis","Prado","Leite",
    "Ramos","Peixoto","Andrade","Maia","Duarte","Sousa","Torres","Moura","Xavier","Freitas",
]

def gerar_nomes_unicos(qtd: int, genero: str) -> list[str]:
    primeiros = FIRST_MALE if genero == 'M' else FIRST_FEMALE
    combos = [f"{p} {s1} {s2}" for p in primeiros for s1 in SOBRENOMES_A for s2 in SOBRENOMES_B]
    random.shuffle(combos)
    return combos[:qtd]

# ======================================================
class Command(BaseCommand):
    help = "Seed de acordo com o modelo atual: catálogo global de grupos/cores e ministérios, casais + servos vinculados, alocações por evento."

    @transaction.atomic
    def handle(self, *args, **opts):
        self.stdout.write(self.style.MIGRATE_HEADING("==> Seed (modelo novo: catálogos globais + alocações por evento)"))

        # Paróquia
        paroquia, _ = Paroquia.objects.get_or_create(
            nome="Paróquia São José",
            defaults={
                "cidade": "Wanderlândia",
                "estado": "TO",
                "responsavel": "Pe. Islei",
                "email": "paroquia@saojose.local",
                "telefone": "+5563999990000",
                "status": "ativa",
            },
        )

        # Admin
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@sistema.local",
                password="admin123",
                tipo_usuario="admin_geral",
            )

        PoliticaPrivacidade.objects.get_or_create(id=1, defaults={"texto": "Política de privacidade (demo)."})
        CrachaTemplate.objects.get_or_create(nome="Padrão - 4 por página")
        for nome in ["ECC","RCC","Pastoral do Dízimo","Catequese","Liturgia","Música"]:
            PastoralMovimento.objects.get_or_create(nome=nome)

        di, df, inicio_ins, fim_ins = periodo(20, 3)

        # ===== Evento principal (CASAIS) — permitir servos =====
        evento_casais, created = EventoAcampamento.objects.get_or_create(
            nome=NOME_CASAIS,
            tipo="casais",
            paroquia=paroquia,
            defaults={
                "data_inicio": di,
                "data_fim": df,
                "inicio_inscricoes": inicio_ins,
                "fim_inscricoes": fim_ins,
                "valor_inscricao": Decimal("150.00"),
                "slug": slugify(f"casais-{NOME_CASAIS}-{di}")[:50],
                "permitir_inscricao_servos": True,
            },
        )
        if not getattr(evento_casais, "permitir_inscricao_servos", False):
            evento_casais.permitir_inscricao_servos = True
            evento_casais.save(update_fields=["permitir_inscricao_servos"])

        PoliticaReembolso.objects.get_or_create(
            evento=evento_casais,
            defaults={"ativo": True, "permite_reembolso": True, "prazo_solicitacao_dias": 7, "descricao": "Reembolso integral até 7 dias antes."}
        )
        VideoEventoAcampamento.objects.get_or_create(
            evento=evento_casais, defaults={"titulo": f"Chamada — {NOME_CASAIS}"[:255]}
        )

        # ===== Evento de SERVOS é criado automaticamente pelo post_save do seu modelo
        evento_servos = evento_casais.servos_evento
        if not evento_servos:
            # fallback: se não veio, cria manualmente
            evento_servos, _ = EventoAcampamento.objects.get_or_create(
                nome=f"Servos – {evento_casais.nome}",
                tipo="servos",
                paroquia=paroquia,
                defaults={
                    "data_inicio": evento_casais.data_inicio,
                    "data_fim": evento_casais.data_fim,
                    "inicio_inscricoes": evento_casais.inicio_inscricoes,
                    "fim_inscricoes": evento_casais.fim_inscricoes,
                    "valor_inscricao": Decimal("0.00"),
                    "slug": slugify(f"servos-{evento_casais.slug}")[:50],
                    "evento_relacionado": evento_casais,
                },
            )
        PoliticaReembolso.objects.get_or_create(
            evento=evento_servos,
            defaults={"ativo": True, "permite_reembolso": False, "prazo_solicitacao_dias": 0, "descricao": "Não há reembolso para servos."}
        )
        VideoEventoAcampamento.objects.get_or_create(
            evento=evento_servos, defaults={"titulo": f"Chamada — {evento_servos.nome}"[:255]}
        )

        # ===== Catálogo global de GRUPOS (com cores)
        grupos_catalogo = {}
        for nome, hexcor in GRUPOS_FIXOS:
            g, _ = Grupo.objects.get_or_create(nome=nome, defaults={"cor_nome": nome, "cor_hex": hexcor})
            # se já existia sem coerência, garantir
            if g.cor_nome != nome or not g.cor_hex:
                g.cor_nome = nome
                g.cor_hex = hexcor
                g.save(update_fields=["cor_nome","cor_hex"])
            grupos_catalogo[nome] = g

        # ===== Catálogo global de MINISTÉRIOS
        ministerios_catalogo = {}
        for nome in MINISTERIOS_FIXOS:
            m, _ = Ministerio.objects.get_or_create(nome=nome, defaults={"descricao": f"Ministério de {nome}", "ativo": True})
            ministerios_catalogo[nome] = m

        # ===== Nomes completos e únicos
        nomes_homens = gerar_nomes_unicos(20, 'M')
        nomes_mulheres = gerar_nomes_unicos(20, 'F')

        # ===== Inscrições de CASAIS
        casais = []
        for i in range(20):
            nm = nomes_homens[i]
            nf = nomes_mulheres[i]
            cidade = CIDADES_TO[i % len(CIDADES_TO)]

            p1, _ = Participante.objects.get_or_create(
                cpf=cpf_fake(i*2 + 1),
                defaults={
                    "nome": nm,
                    "telefone": f"+5563999{i:07d}"[:15],
                    "email": f"casal{i+1}.ele@example.com",
                    "CEP": "77860-000",
                    "endereco": "Rua Principal", "numero": "100",
                    "bairro": "Centro", "cidade": cidade, "estado": "TO",
                },
            )
            p2, _ = Participante.objects.get_or_create(
                cpf=cpf_fake(i*2 + 2),
                defaults={
                    "nome": nf,
                    "telefone": f"+5563998{i:07d}"[:15],
                    "email": f"casal{i+1}.ela@example.com",
                    "CEP": "77860-000",
                    "endereco": "Rua Principal", "numero": "100",
                    "bairro": "Centro", "cidade": cidade, "estado": "TO",
                },
            )

            ins1, _ = Inscricao.objects.get_or_create(
                participante=p1, evento=evento_casais,
                defaults={"paroquia": paroquia, "status": InscricaoStatus.ENVIADA}
            )
            ins2, _ = Inscricao.objects.get_or_create(
                participante=p2, evento=evento_casais,
                defaults={"paroquia": paroquia, "status": InscricaoStatus.ENVIADA}
            )

            # cria bases casais (seu BaseInscricao específico)
            InscricaoCasais.objects.get_or_create(inscricao=ins1, defaults={"paroquia": paroquia, "data_nascimento": date(1990,1,1)})
            InscricaoCasais.objects.get_or_create(inscricao=ins2, defaults={"paroquia": paroquia, "data_nascimento": date(1990,1,1)})

            # parear (modelo já garante consistência)
            try:
                ins1.set_pareada(ins2)
            except Exception:
                pass

            # estados: 8 confirmados, 4 pendentes, 8 enviados
            if i < 8:
                alvo = InscricaoStatus.PAG_CONFIRMADO
            elif i < 12:
                alvo = InscricaoStatus.PAG_PENDENTE
            else:
                alvo = InscricaoStatus.ENVIADA

            for ins in (ins1, ins2):
                fast_status(ins, alvo)
                if alvo in (InscricaoStatus.PAG_CONFIRMADO, InscricaoStatus.PAG_PENDENTE):
                    ensure_pagamento(
                        ins,
                        confirmado=(alvo == InscricaoStatus.PAG_CONFIRMADO),
                        valor=evento_casais.valor_inscricao or Decimal("0.00"),
                    )

            casais.append((ins1, ins2))

        # ===== SERVOS: usar 8 casais (16 pessoas) como servos
        servos_fontes = []
        for k in range(8):
            servos_fontes.extend([casais[k][0], casais[k][1]])

        grupos_lista = [grupos_catalogo[n] for n in ["Amarelo","Vermelho","Azul","Verde"]]
        ministros_lista = [ministerios_catalogo[n] for n in MINISTERIOS_FIXOS]

        for idx, src_ins in enumerate(servos_fontes):
            # cria inscrição no evento de servos (valida permitir_inscricao_servos)
            ins_sv, _ = Inscricao.objects.get_or_create(
                participante=src_ins.participante,
                evento=evento_servos,
                defaults={"paroquia": paroquia, "status": InscricaoStatus.CONVOCADA}
            )

            # Alocação de Grupo (precisa de evento=servos)
            AlocacaoGrupo.objects.get_or_create(
                inscricao=ins_sv,
                evento=evento_servos,
                defaults={"grupo": grupos_lista[idx % len(grupos_lista)]},
            )

            # Alocação de Ministério (um coordenador por (evento, ministério))
            mref = ministros_lista[idx % len(ministros_lista)]
            is_coord = not AlocacaoMinisterio.objects.filter(evento=evento_servos, ministerio=mref, is_coordenador=True).exists()
            AlocacaoMinisterio.objects.get_or_create(
                inscricao=ins_sv,
                evento=evento_servos,
                defaults={"ministerio": mref, "funcao": "Serviço", "is_coordenador": is_coord},
            )

        self.stdout.write(self.style.SUCCESS(
            "OK: Casais (nomes completos e únicos) + Servos criados. Grupos/cores e Ministérios do catálogo aplicados nas alocações do evento de servos."
        ))
        self.stdout.write(self.style.SUCCESS("Login admin/admin123 (se necessário)."))
