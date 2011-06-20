from django.contrib import admin
from lti.jatic.models import Inscricao, Palestrante, Atracao, Alocacao

class InscricaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'pago', 'notificado')
    list_filter = ('pago', 'notificado')
    
class PalestranteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'admin_thumbnail',)    

class AtracaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'vagas', 'horaInicio', 'horaFim')

class AlocacaoAdmin(admin.ModelAdmin):
    list_display = ('atracao', 'inscricao')

admin.site.register(Inscricao, InscricaoAdmin)
admin.site.register(Palestrante, PalestranteAdmin)
admin.site.register(Atracao, AtracaoAdmin)
admin.site.register(Alocacao, AlocacaoAdmin)
