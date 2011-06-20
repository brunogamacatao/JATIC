from django.conf.urls.defaults import *

urlpatterns = patterns('lti.jatic.views',
    (r'^$', 'index'),
    (r'^inscricao/$', 'inscricao'),
    (r'^palestrantes/$', 'palestrantes'),
    (r'^programacao/$', 'programacao'),
    (r'^localizacao/$', 'localizacao'),
    (r'^contato/$', 'contato'),
    (r'^retorno/$', 'retorno'),
    (r'^confirma/(?P<id_inscricao>\d+)$', 'confirma'),
    (r'^matricula/(?P<id_inscricao>\d+)/(?P<id_atracao>\d+)$', 'matricula'),
    (r'^desistir/(?P<id_inscricao>\d+)/(?P<id_atracao>\d+)$', 'desistir'),
    (r'^enviaEmail/$', 'enviaEmail'),
    (r'^evento/$', 'eventos'),
    (r'^evento/(?P<id_evento>\d+)$', 'evento'),
    (r'^twitter_signin/$', 'twitter_signin'),
    (r'^twitter_return/$', 'twitter_return'),
    (r'^twitter_follow_me/$', 'twitter_follow_me'),
)

