# Predicción del tiempo de la AEMET
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/jvt1963/snips-turnOnOff-http/master/LICENSE)

Permite preguntar por la predicción meteorológica de los próximos 7 días.
Los datos se extraen de las predicciones por municipio de la AEMET.
Se puede preguntar por la predicción del tiempo completa ("¿Qué tiempo va a hacer hoy en Madrid?") o únicamente por el estado del cielo ("¿Cómo va a estar el cielo mañana en Segovia?"), previsiones de lluvia ("¿Va a llover pasado mañana en Santander?"), cota de nieve, humedad y viento.
En el archivo municipios.py se puede configurar el municipio por defecto (la predicción se referirá a ese municipio cuando no se indique en la petición ningún municipio o cuando snips no entienda el que se indique.
Si no se indica la fecha la respuesta se referirá a las predicciones del día.
