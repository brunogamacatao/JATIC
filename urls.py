from django.conf import settings
from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^sebrae/', include('lti.sebrae.urls')),
    (r'^olimpiada/', include('lti.olimpiada.urls')),
    (r'^jatic/', include('lti.jatic.urls')),
    (r'^csw/', include('lti.csw.urls')),
    (r'^vestibular/', include('lti.vestibular.urls')),
    (r'^censo/', include('lti.censo.urls')),
#    (r'^eleicao/', include('lti.eleicao.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^boleto/', include('djboleto.boleto.urls')),
    (r'^boleto_bb/$', 'djboleto.boleto.views.boleto_bb'),
    (r'^boleto_caixa/$', 'djboleto.boleto.views.boleto_caixa'),
    (r'^boleto_real/$', 'djboleto.boleto.views.boleto_real'),
    (r'^boleto_bnb/$', 'djboleto.boleto.views.boleto_bnb'),
    (r'^boleto_bradesco/$', 'djboleto.boleto.views.boleto_bradesco'),
)
