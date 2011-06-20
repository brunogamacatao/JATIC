from django.core.management.base import BaseCommand, CommandError
from twitterauth.oauthtwitter import OAuthApi
from BeautifulSoup import BeautifulSoup
import urllib2
import datetime

# These keys must be for one client application
consumer_key    = "ziTuHQjXceXR1LTevu0YQ"
consumer_secret = "Uhjmyb4dvCFCnC2NSsB0VcpUKTebTNhhqqH6Qr4"

class Programa(object):
    def __init__(self, hora, nome):
        self.hora = hora
        self.nome = nome

    def __repr__(self):
        return '%s - %s' % (self.hora, self.nome)

class Command(BaseCommand):
    def handle(self, *args, **options):
        print 'Autenticando no twitter ...'
        access_token = {'oauth_token': '217494643-NCcUY36uQZJXTWtfiPfkPdugIPysjtluDDGkdybb', 'oauth_token_secret': '8qskSfAkciPFCDHhmyVwcpGSDFezNJ3ruRLeCnDWT4'}
        twitter = OAuthApi(consumer_key, consumer_secret, access_token['oauth_token'], access_token['oauth_token_secret'])
        print 'Pronto'

        programas = []

        print 'Obtendo a lista de programas ...'
        resp = urllib2.urlopen('http://canalfox.com.br/br/programacao/%s' % (datetime.datetime.now().strftime('%Y-%m-%d')))
        soup = BeautifulSoup(resp.read())
        for programa in soup.find('div', {'class': 'content-primary', }).find('ul').findAll('li'):
            dados = programa.a.text
            hora  = [int(i) for i in dados[0:5].split(':')]
            nome  = dados[5:].encode('utf-8')
            programas.append(Programa(datetime.time(hora[0], hora[1]), nome))

        print '%d programas adicionados' % (len(programas), )
        print 'Verificando se ha alguma notificacao a fazer ...'
        agora = datetime.datetime.now().time()
        print 'Hora atual: %s' % (agora)
        # Hack necessario por causa do horario de verao, tirar isso apos terminado o DST
        agora = datetime.time(agora.hour + 1, agora.minute)
        print 'Hora DST: %s' % (agora)
        # Fim do hack

        #Obtendo a lista de seguidores
        print 'Obtendo a lista de seguidores ...'
        seguidores = twitter.GetFollowers()
        for seguidor in seguidores:
            print seguidor['screen_name']

        for programa in programas:
            if agora <= programa.hora and 'Simpsons' in programa.nome:
                diff = (programa.hora.hour * 60 + programa.hora.minute) - (agora.hour * 60 + agora.minute)
                if (diff <= 5): #Se a diferenca for menor que 5 minutos
                    print u'O programa %s vai comecar logo logo (as %s), notificando os interessados ...' % (programa.nome, programa.hora, )
                    msg = u'%s vai comecar as %s' % (programa.nome, programa.hora, )
                    for seguidor in seguidores:
                        twitter.ApiCall('direct_messages/new', 'POST', {'screen_name': seguidor['screen_name'], 'text': msg, })

