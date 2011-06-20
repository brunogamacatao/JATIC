# -*- coding: iso-8859-1 -*-
import re
from django import forms
from django.forms import ModelForm
from lti.jatic.models import Inscricao, Contato

TELEFONE_RE = re.compile(r'^\([0-9]{2}\)[0-9]{4}-[0-9]{4}')

class InscricaoForm(ModelForm):
    telefone = forms.RegexField(TELEFONE_RE, max_length=13, min_length=13, required=True, label=u'Telefone:')
    class Meta:
        model = Inscricao
        exclude = ['pago', 'notificado']
        
class ContatoForm(ModelForm):
    telefone = forms.RegexField(TELEFONE_RE, max_length=13, min_length=13, required=True, label=u'Telefone:')
    class Meta:
        model = Contato
