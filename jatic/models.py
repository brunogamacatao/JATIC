# -*- coding: iso-8859-1 -*-
from django.db import models
from django.conf import settings
import Image, os

THUMB_SIZE = (88, 88)

ESTADOS_CHOICES = (
    ('', u'Selecione um estado'),
    ('AC', u'Acre'),
    ('AL', u'Alagoas'),
    ('AP', u'Amapá'),
    ('AM', u'Amazonas'),
    ('BA', u'Bahia'),
    ('CE', u'Ceará'),
    ('DF', u'Distrito Federal'),
    ('ES', u'Espírito Santo'),
    ('GO', u'Goiás'),
    ('MA', u'Maranhão'),
    ('MT', u'Mato Grosso'),
    ('MS', u'Mato Grosso do Sul'),
    ('MG', u'Minas Gerais'),
    ('PA', u'Pará'),
    ('PB', u'Paraíba'),
    ('PR', u'Paraná'),
    ('PE', u'Pernambuco'),
    ('PI', u'Piauí'),
    ('RR', u'Roraima'),
    ('RO', u'Rondônia'),
    ('RJ', u'Rio de Janeiro'),
    ('RN', u'Rio Grande do Norte'),
    ('RS', u'Rio Grande do Sul'),
    ('SC', u'Santa Catarina'),
    ('SP', u'São Paulo'),
    ('SE', u'Sergipe'),
    ('TO', u'Tocantins'),
)

class Inscricao(models.Model):
    nome        = models.CharField(blank=False, max_length=100)
    endereco    = models.CharField(blank=False, max_length=100, verbose_name=u'Endereço')
    numero      = models.CharField(blank=False, max_length=10, verbose_name=u'Número')
    complemento = models.CharField(blank=True, max_length=100)
    bairro      = models.CharField(blank=False, max_length=100)
    cep         = models.CharField(blank=False, max_length=9)
    cidade      = models.CharField(blank=False, max_length=100)
    estado      = models.CharField(blank=False, max_length=2, choices=ESTADOS_CHOICES)
    telefone    = models.CharField(blank=False, max_length=13) #Extrair o DDD automaticamente
    email       = models.EmailField(blank=False)
    pago        = models.BooleanField(blank=True, default=False)
    notificado  = models.BooleanField(blank=True, default=False)

    class Meta:
        verbose_name        = u"Inscrição"
        verbose_name_plural = u"Inscrições"
        ordering = ('nome', )

    def __unicode__(self):
        return '%s' % (self.nome)
  
def handle_thumb(image_obj, thumb_obj, width, height):
    # create thumbnail
    if image_obj and not thumb_obj:
        thumb = image_obj.path + ('-t%sx%s.png' % (width, height))
        t = Image.open(image_obj.path)

        w, h = t.size
        if float(w)/h < float(width)/height:
            t = t.resize((width, h*width/w), Image.ANTIALIAS)
        else:
            t = t.resize((w*height/h, height), Image.ANTIALIAS)
        w, h = t.size
        t = t.crop( ((w-width)/2, (h-height)/4, (w-width)/2+width, (h-height)/4+height) )

        t.save(thumb, 'PNG')
        os.chmod(thumb, 0666)
        thumb_obj = thumb
    return thumb_obj
        
class Palestrante(models.Model):
    nome      = models.CharField(blank=False, max_length=100)
    biografia = models.TextField()
    foto      = models.ImageField(upload_to='jatic/images/%Y%m%d')
    thumbnail = models.ImageField(upload_to='jatic/images/%Y%m%d', editable=False)
    
    def save(self):
        super(Palestrante, self).save()
        self.thumbnail = handle_thumb(self.foto, self.thumbnail, THUMB_SIZE[0], THUMB_SIZE[1])
        super(Palestrante, self).save()
    
    def admin_thumbnail(self):
        if self.thumbnail:
            return '<a href="%s"><img src="%s-t%dx%d.png" alt=""></a>' % (self.foto.url, self.foto.url, THUMB_SIZE[0], THUMB_SIZE[1])
        return None
   
    def __unicode__(self):
        return self.nome
 
    admin_thumbnail.allow_tags = True
    admin_thumbnail.short_description = 'foto'

class Contato(models.Model):
    nome     = models.CharField(blank=False, max_length=100)
    email    = models.EmailField(blank=False)
    telefone = models.CharField(blank=False, max_length=13)
    mensagem = models.TextField(blank=False)

class Atracao(models.Model):
    nome = models.CharField(blank=False, max_length=100)
    palestrante = models.ForeignKey(Palestrante, blank=False)
    horaInicio = models.DateTimeField(blank=False)
    horaFim    = models.DateTimeField(blank=False)
    vagas      = models.IntegerField(blank=False)

    def __unicode__(self):
        return self.nome

    class Meta:
        verbose_name        = u"Atração"
        verbose_name_plural = u"Atrações"

class Alocacao(models.Model):
    inscricao = models.ForeignKey(Inscricao, blank=False)
    atracao   = models.ForeignKey(Atracao, blank=False)
    class Meta:
        verbose_name        = u"Alocação"
        verbose_name_plural = u"Alocações"

