from django import forms

class SimNaoRadioSelect(forms.RadioSelect):
    template_name = 'inscricoes/widgets/sim_nao_radio.html'

    def __init__(self, *args, **kwargs):
        choices = (('True', 'Sim'), ('False', 'Não'))
        super().__init__(choices=choices, *args, **kwargs)