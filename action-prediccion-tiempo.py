#!/usr/bin/env python3
from hermes_python.hermes import Hermes
import hermes_python 
import requests
from municipios import defaultmunicipio, nombremunicipio, urlmunicipio
from xml.etree import ElementTree as ET
from datetime import datetime, date, time, timedelta
import calendar

MQTT_IP_ADDR = "localhost" 
MQTT_PORT = 1883 
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT)) 

a = datetime.now()
f = a.date()
defaultfecha = str(f)


def select_url(current_municipio):
    for x in nombremunicipio:
        if x == current_municipio:
            break
    idxm = nombremunicipio.index(x)
    urlm = urlmunicipio[idxm]
    return urlm


def presentar_periodo(x):
    if x == '00-24':
        frase = 'Durante el día '
    elif x == '00-12':
        frase = 'Antes de mediodía '
    elif x == '12-24':
        frase = 'En la segunda mitad del día '
    elif x == '00-06':
        frase = 'En la madrugada '
    elif x == '06-12':
        frase = 'Durante la mañana '
    elif x == '12-18':
        frase = 'A primera hora de la tarde '
    elif x == '18-24':
        frase = 'Al anochecer '
    else:
        frase = ''
    return frase


def pred_cielo(hoy):
    for estado_cielo in hoy.iter('estado_cielo'):
        if estado_cielo.get('descripcion'):
            per = estado_cielo.get('periodo')
            fr_periodo = presentar_periodo(per)
            p_cielo = fr_periodo + "el estado del cielo será " + estado_cielo.get('descripcion') + ". "
            break
    return p_cielo


def pred_temperatura(hoy):
    t = hoy.find('temperatura')
    tmax = t.find('maxima').text
    tmin = t.find('minima').text
    s = hoy.find('sens_termica')
    smax = s.find('maxima').text
    smin = s.find('minima').text
    p_temperatura =  "La temperatura máxima será de " + tmax + " grados, con una sensación térmica de " + smax + ". La mínima será de " + tmin + " grados, con una sensación térmica de " + smin + ". "
    return p_temperatura


def pred_humedad(hoy):
    h = hoy.find('humedad_relativa')
    hmax = h.find('maxima').text
    hmin = h.find('minima').text
    p_humedad =  "La humedad relativa oscilará entre " + hmin + " y " + hmax + " por ciento. "
    return p_humedad


def pred_lluvia(hoy):
    for prob_precipitacion in hoy.iter('prob_precipitacion'):
        if prob_precipitacion.text:
            per = prob_precipitacion.get('periodo')
            fr_periodo = presentar_periodo(per)
            if prob_precipitacion.text == '0':
                p_lluvia = fr_periodo + "no se prevé lluvia. "
            else:
                p_lluvia = fr_periodo + "la probabilidad de lluvia es del " + prob_precipitacion.text + " por ciento. "
            break
    return p_lluvia


def pred_nieve(hoy):
    p_nieve = ''
    for cota_nieve_prov in hoy.iter('cota_nieve_prov'):
        if cota_nieve_prov.text:
            per = cota_nieve_prov.get('periodo')
            fr_periodo = presentar_periodo(per)
            p_nieve = fr_periodo + "la cota de nieve en la provincia se situará en " + cota_nieve_prov.text + " metros. "
            break
    return p_nieve


def pred_viento(hoy):
    for viento in hoy.iter('viento'):
        dv = viento.find('direccion')
        vv = viento.find('velocidad')
        if dv.text:
            dirv = dv.text
            velv = vv.text
            per = viento.get('periodo')
            fr_periodo = presentar_periodo(per)
            break

    if dirv == 'N':
        p_viento = fr_periodo + 'el viento será del Norte, velocidad ' + velv + ' kilómetros por hora. '
    if dirv == 'NE':
        p_viento = fr_periodo + 'el viento será del Noreste, velocidad ' + velv + ' kilómetros por hora. '
    if dirv == 'NO':
        p_viento = fr_periodo + 'el viento será del Noroeste, velocidad ' + velv + ' kilómetros por hora. '
    if dirv == 'S':
        p_viento = fr_periodo + 'el viento será del Sur, velocidad ' + velv + ' kilómetros por hora. '
    if dirv == 'SE':
        p_viento = fr_periodo + 'el viento será del Sureste, velocidad ' + velv + ' kilómetros por hora. '
    if dirv == 'SO':
        p_viento = fr_periodo + 'el viento será del Suroeste, velocidad ' + velv + ' kilómetros por hora. '
    if dirv == 'E':
        p_viento = fr_periodo + 'el viento será del Este, velocidad ' + velv + ' kilómetros por hora. '
    if dirv == 'O':
        p_viento = fr_periodo + 'el viento será del Oeste, velocidad ' + velv + ' kilómetros por hora. '
    if dirv == 'C':
        p_viento = fr_periodo + 'la situación será de calma. '

    for racha_max in hoy.iter('racha_max'):
        if racha_max.text:
            per = racha_max.get('periodo')
            fr_periodo = presentar_periodo(per)
            p_viento += "Con rachas máximas de " + racha_max.text + " kilómetros por hora. "
            break
    return p_viento



def intent_received(hermes, intentMessage):

    if intentMessage.intent.intent_name == 'jaimevegas:DiTiempo':

        try:
            clima = intentMessage.slots.Clima.first().value
        except TypeError:
            clima = 'tiempo'
            pass

        try:
            municipio = intentMessage.slots.Municipio.first().value
        except TypeError:
            municipio = defaultmunicipio
            pass

        if intentMessage.slots.Fecha:
            tmp = intentMessage.slots.Fecha[0].slot_value.value
            fr_fecha = intentMessage.slots.Fecha[0].raw_value

        try:
            if isinstance(tmp, hermes_python.ontology.dialogue.InstantTimeValue):
                val = tmp.value[:-7]
                diapred = val[0:10]
        except UnboundLocalError:
            diapred = defaultfecha
            fr_fecha = 'hoy'
            pass

        url = select_url(municipio)
        response = requests.get(url)
        xml = response.text
        root = ET.fromstring(xml)

        prediccion = root.find('prediccion')
        for dia in prediccion.iter('dia'):
            if dia.get('fecha') == diapred:
                hoy = dia
                break

        pc = pred_cielo(hoy)
        pt = pred_temperatura(hoy)
        ph = pred_humedad(hoy)
        pl = pred_lluvia(hoy)
        pn = pred_nieve(hoy)
        pv = pred_viento(hoy)


        sentence = 'La predicción de ' + clima + ' en ' + municipio + ' para ' + fr_fecha + ' según la Agencia Estatal de Meteorología es la siguiente: '

        if clima == 'cielo':
            sentence +=  pc
        if clima == 'temperatura':
            sentence +=  pt
        if clima == 'humedad':
            sentence +=  ph
        if clima == 'lluvia':
            sentence +=  pl + pn
        if clima == 'nieve':
            sentence +=  pn
        if clima == 'viento':
            sentence +=  pv
        if clima == 'tiempo':
            sentence +=  pc + pt + pl + pn + ph + pv

    else:
        return
    
    hermes.publish_end_session(intentMessage.session_id, sentence)
    
    
with Hermes(MQTT_ADDR) as h:
    h.subscribe_intents(intent_received).start()
