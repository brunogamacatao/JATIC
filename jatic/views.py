# -*- coding: utf-8 -*-
import re
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.views.generic.simple import direct_to_template

from django.template import Context
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives

from lti.jatic.models import *
from lti.jatic.forms import InscricaoForm, ContatoForm

from lti.pagseguro.util import telefone as split_telefone
from lti.pagseguro.retorno import retorno as ret_pagseguro
from lti.utils.pagamentolib import PagSeguro

def index(request):
    return direct_to_template(request, 'jatic/index.html')

def palestrantes(request):
    params = {'palestrantes': Palestrante.objects.order_by('nome'),}
    return direct_to_template(request, 'jatic/palestrantes.html', params)

def localizacao(request):
    return direct_to_template(request, 'jatic/localizacao.html')

def programacao(request):
    return direct_to_template(request, 'jatic/programacao.html')

@csrf_protect
def contato(request):
    form = None

    if request.method == 'GET':
        form = ContatoForm()
    else:
        form = ContatoForm(request.POST)
        if form.is_valid():
            contato = form.save()
            enviaEmailContato(contato)
            return direct_to_template(request, 'jatic/contato_enviado.html')
            
    return direct_to_template(request, 'jatic/contato.html', {'form': form})
    
def limpa_texto(str):
    if not str:
        return str
    str = str.upper()
    str = re.sub('[ÁÀÃÄÂ]', 'A', str)
    str = re.sub('[ÉËÊ]', 'E', str)
    str = re.sub('[ÍÏ]', 'I', str)
    str = re.sub('[ÓÖÔÕ]', 'O', str)
    str = re.sub('[ÚÜ]', 'U', str)
    str = re.sub('[Ç]', 'C', str)
    str = re.sub('[^A-Z0-9\\s]', '', str)
    return str
    
def enviaEmailConfirmacao(email):
    subject = u'JATIC'
    from_email = 'suporte@lti.cesed.br'

    params = {}
    
    text_content = get_template('jatic/emails/email_confirmacao.txt').render(Context(params))
    html_content = get_template('jatic/emails/email_confirmacao.html').render(Context(params))
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, [email,])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def enviaEmailContato(contato):
    subject = u'[JATIC] Contato'
    from_email = 'suporte@lti.cesed.br'

    params = {'contato': contato}
    
    text_content = get_template('jatic/emails/email_contato.txt').render(Context(params))
    html_content = get_template('jatic/emails/email_contato.html').render(Context(params))
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, [contato.email,])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

@csrf_protect
def inscricao(request):
    form = None
    
    if request.method == 'GET':
        form = InscricaoForm(initial={'estado':'PB', 'cidade': 'Campina Grande'})
    else:
        form = InscricaoForm(request.POST)
        if form.is_valid():
            inscricao = form.save(commit=False)
            inscricao.pago = True
            inscricao.save()
            return HttpResponseRedirect(reverse('lti.jatic.views.confirma', args=[inscricao.id,]))

            
            #Retirando os acentos devido a restricoes do PagSeguro
#            inscricao.nome        = limpa_texto(inscricao.nome)
#            inscricao.endereco    = limpa_texto(inscricao.endereco)
#            inscricao.numero      = limpa_texto(inscricao.numero)
#            inscricao.complemento = limpa_texto(inscricao.complemento)
#            inscricao.bairro      = limpa_texto(inscricao.bairro)
#            inscricao.cidade      = limpa_texto(inscricao.cidade)
            
#            params = {
#                'dados': inscricao, 
#                'cep': inscricao.cep.replace('-', ''),
#                'ddd': split_telefone(inscricao.telefone)[0], 
#                'telefone': split_telefone(inscricao.telefone)[1]
#            }
            
#            return direct_to_template(request, 'jatic/pagamento.html', params)
    
    return direct_to_template(request, 'jatic/inscricao.html', {'form': form,})

def confirma(data):
    if data['StatusTransacao'] == 'Aprovado':
        inscricao = Inscricao.objects.get(id=data.get('Referencia'))
        inscricao.pago = True
        inscricao.save()
        enviaEmailConfirmacao(inscricao.email)

@csrf_exempt
def retorno(request):
    if request.method == 'POST':
        token = '5E52091DC99E4F26AE172DAB6FCE4E07'
        try:
            ret_pagseguro(request.POST, token, confirma)
            return HttpResponse("ok")
        except:
            return HttpResponse("error")
    else:
        return direct_to_template(request, 'jatic/status_pagto.html', {'status': u'Em processamento'})

@csrf_protect
def confirma(request, id_inscricao):
    inscricao = Inscricao.objects.get(id=id_inscricao)
    form = InscricaoForm(instance=inscricao)
    if request.POST:
        form = InscricaoForm(request.POST, instance=inscricao)
        if form.is_valid():
            inscricao = form.save()
    atracoes_disponiveis  = [atracao for atracao in Atracao.objects.filter(vagas__gte=0).order_by('horaInicio', 'horaFim')]
    atracoes_selecionadas = [alocacao.atracao for alocacao in Alocacao.objects.filter(inscricao=inscricao)]
    # Removendo as atracoes que ja foram selecionadas
    for atracao in atracoes_selecionadas:
        atracoes_disponiveis.remove(atracao)
    # Removendo as atracoes com choques de horario
    for i in range(4):
        for a1 in atracoes_selecionadas:
            for a2 in atracoes_disponiveis:
                if a2.horaInicio >= a1.horaInicio and a2.horaInicio <= a1.horaFim:
                    atracoes_disponiveis.remove(a2) 

    return direct_to_template(request, 'jatic/confirma.html', {'form': form, 'inscricao': inscricao, 'atracoes_disponiveis': atracoes_disponiveis, 'atracoes_selecionadas': atracoes_selecionadas}) 

def matricula(request, id_inscricao, id_atracao):
    inscricao = Inscricao.objects.get(id=id_inscricao)
    atracao   = Atracao.objects.get(id=id_atracao)
    alocacao  = Alocacao(inscricao=inscricao, atracao=atracao)
    if atracao.vagas > 0:
        atracao.vagas -= 1
        atracao.save()
        alocacao.save()
    return HttpResponseRedirect(reverse('lti.jatic.views.confirma', args=[id_inscricao,]))

def desistir(request, id_inscricao, id_atracao):
    inscricao = Inscricao.objects.get(id=id_inscricao)
    atracao   = Atracao.objects.get(id=id_atracao)
    alocacao  = Alocacao.objects.get(inscricao=inscricao, atracao=atracao)
    atracao.vagas += 1
    atracao.save()
    alocacao.delete()
    return HttpResponseRedirect(reverse('lti.jatic.views.confirma', args=[id_inscricao,]))

def enviaEmail(request):
    qtd = 0
    for inscricao in Inscricao.objects.filter(pago=True, notificado=False):
        subject = u'[JATIC 2010] Inscreva-se nas palestras e mini-cursos'
        from_email = 'suporte@lti.cesed.br'
        
        text_msg = u'''
Prezado(a) %s,

Acesse o link http://lti.cesed.br/apps/jatic/confirma/%d para se inscrever nas palestras e mini-cursos do JATIC 2010.
Aproveite também para conferir se seus dados pessoais estão corretos, pois os mesmos serão utilizados para a confecção dos crachás e certificados.

Cumprimentos,
A organização do JATIC.
''' % (inscricao.nome, inscricao.id)
        msg = EmailMultiAlternatives(subject, text_msg, from_email, [inscricao.email,])
        msg.send()
        inscricao.notificado = True
        inscricao.save()
        qtd += 1
    return HttpResponse('%d emails foram enviados' % (qtd,))

def eventos(request):
    return direct_to_template(request, 'jatic/eventos.html', {'eventos': Atracao.objects.order_by('horaInicio', 'horaFim'),})

def evento(request, id_evento):
    return direct_to_template(request, 'jatic/evento.html', {'evento': Atracao.objects.get(id=id_evento),})

from lti.jatic.utils import *
import simplejson

CONSUMER_KEY    = getattr(settings, 'CONSUMER_KEY')
CONSUMER_SECRET = getattr(settings, 'CONSUMER_SECRET')

CONSUMER = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)

def twitter_signin(request):
    token = get_unauthorised_request_token(CONSUMER)
    auth_url = get_authorisation_url(CONSUMER, token)
    request.session['unauthed_token'] = token.to_string()
    return HttpResponseRedirect(auth_url)

def twitter_return(request):
    unauthed_token = request.session.get('unauthed_token', None)
    token = oauth.OAuthToken.from_string(unauthed_token)
    access_token = exchange_request_token_for_access_token(CONSUMER, token)
    request.session['access_token'] = access_token.to_string()
    is_authenticated(CONSUMER, access_token)
    return HttpResponseRedirect(reverse('lti.jatic.views.twitter_follow_me'))

def twitter_follow_me(request):
    access_token = request.session.get('access_token', None)
    token = oauth.OAuthToken.from_string(access_token)
    auth = is_authenticated(CONSUMER, token)
    creds = simplejson.loads(auth)
    result = follow(CONSUMER, token, 'lembres', '217494643')
    return HttpResponse('Voce esta seguindo o lembres no twitter e recebera notificacoes automaticamente. Resultado: %s ' % (result, ))
