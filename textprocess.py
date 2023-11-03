import spacy
from word2number_es import w2n
import re
import json
from unidecode import unidecode
import difflib
from spellchecker import SpellChecker
nlp = spacy.load("es_core_news_sm")
stop_words = set(spacy.lang.es.STOP_WORDS)
spell = SpellChecker(language='es') 

comandos1 = ["agregar" , "buscar", "desactivar", "actualizar","mostrar","vender","vendi","anadir" ]
comandos2= ["inca kola", "coca cola", "fanta", "san luis", "galleta", "rellenita","san mateo", "cielo", "gaseosa", "galleta" ]
comandos3 = ["precio", "costo", "a", "salio"]
comandos4 = ["cantidad", "compre" , "recibi", "producto"]
comandos5= ["litro", "mililitro","gramo","kilo","kilogramo", "soles", "centimos", "sol"]
comandos6 = ["docena", "decena", "centena", "media", "cuarto", "tercio"]

dictionary = w2n.NUMBER_WORDS + comandos1 + comandos2+comandos3+comandos4+comandos5+comandos6

def return_price(precio):
    if precio:
        precio_decimal = 0.0
        precio_tokens = precio.lower().split()
        for i in range(len(precio_tokens)):
            if precio_tokens[i] == "soles" or precio_tokens[i] == "sol":
                precio  = " ".join(precio_tokens[:i])
                precio_decimal = w2n.word_to_num(precio)
                try:
                   centimos = " ".join(precio_tokens[i+1:])
                   cent = w2n.word_to_num(centimos)
                   precio_decimal += w2n.word_to_num(centimos) /100

                except:
                  return precio_decimal

            elif precio_tokens[i] == "centimos" or precio_tokens[i] == "centimo":
                if "soles" not in precio_tokens[:i] or "sol" not in precio_tokens[:i] :
                    precio  = " ".join(precio_tokens[:i])
                    precio_decimal += w2n.word_to_num(precio) / 100
        return precio_decimal

unidad_abreviacion = {
    "litro": "L",
    "mililitro": "ml",
    "gramo": "g",
    "kilo": "kg",
    "kilogramo": "kg",
}


frases_especiales = {
    "medio litro": "500 mL",
    "personal": "500 mL",  # Agrega otras frases especiales aquí
}

def buscar_singular(palabra):
    palabra_singular = unidad_abreviacion.get(palabra, palabra)
    return palabra_singular

def procesar_frase_especial(frase):
    return frases_especiales.get(frase, frase) 


def return_cantidad(cantidad):

    operaciones = {
    "media docena": lambda numero: numero * 6,
    "docena media": lambda numero: numero * 12 + 6,
    "docena": lambda numero: numero * 12,
    "decena": lambda numero: numero * 10,
    "decena media": lambda numero: numero * 10 + 5,
    "media decena": lambda numero: numero * 5,
    "cuarto": lambda numero: numero * 3,
    "tercio": lambda numero: numero * 4,
    "media centena": lambda numero: numero * 50,
    "centena": lambda numero: numero *100,
    }
    if cantidad:
        tokens_cantidad = cantidad.lower().split()
        numero = 0
        tokens_not_recog = []

        for token in tokens_cantidad:
            try:
                num = w2n.word_to_num(token)
                numero += num
            except ValueError:
                tokens_not_recog.append(token)

        doc = nlp(" ".join([token for token in tokens_not_recog if token not in stop_words]))
        keyword = " ".join([token.lemma_.lower() for token in doc])
        if (numero == 0): numero = 1
        if keyword in operaciones:
            operacion = operaciones[keyword]
            resultado = operacion(numero)
            return resultado
        else:
            return numero

def correcion(texto):
  textob = unidecode(texto)
  textoc = textob.split()
  corrected = []
  for i in range(len(textoc)):
    corregido = difflib.get_close_matches(textoc[i], dictionary, n=1, cutoff=0.6)
    if corregido:
      corrected.append(corregido[0])
    else:
      corrected.append(textoc[i])
  oracion_corregida = ' '.join(corrected)
  return oracion_corregida

def procesar_alias(descripcion):
  if descripcion:
    tokens = descripcion.lower().split()
    numeroescr = []
    numero = 0
    totals = []
    nombreproducto = []
    for token in tokens:
        try:
            num = w2n.word_to_num(token)
            numeroescr.append(token)

        except ValueError:
            if token not in unidad_abreviacion:
              token = token.capitalize()
            if( len(numeroescr) > 0):
              for i in range(len(numeroescr)):
                numeroescr[i] = w2n.word_to_num(numeroescr[i])
                numero += numeroescr[i]

              totals.append(numero)
              palabra_procesada = buscar_singular(token)

              totals.append(palabra_procesada)

            else:
                totals.append(token)
    descripcion_procesada = " ".join([str(item) if isinstance(item, int) else item for item in totals])
    return descripcion_procesada



categorias_palabras_clave = {
    "Comando": ["agregar" , "buscar", "desactivar", "actualizar","mostrar","vender","vendi","anadir" ]   ,
    "Producto": ["inca", "coca","fanta", "san", "galleta", "rellenita","san", "agua", "gaseosa", "galleta","agua", "cielo"],
    "Precio": ["precio", "costo", "a", "salio"],
    "Cantidad": ["cantidad", "compre" , "recibi", "vendi"]
}

def recibirjson(texto):

  #texto = correcion(texto)
  doc = nlp(texto)

  comando = ""
  nombre_producto = ""
  precio = ""
  cantidad = ""
  current_key = None

  for token in doc:

      token_text = token.text.lower()
      for categoria, palabras_clave in categorias_palabras_clave.items():
          if token_text in palabras_clave:
              current_key = categoria
              break

      if current_key:
          if current_key == "Comando":
              comando = token.text
              cantidad += " " + token.text
          elif current_key == "Producto":
              nombre_producto += " " + token.text   
          elif current_key == "Precio":
              precio += " " + token.text
          elif current_key == "Cantidad":
              cantidad += " " + token.text


  #nombre_producto = " ".join([word for word in nombre_producto.split() if word not in categorias_palabras_clave["Producto"]])
  precio = " ".join([word for word in precio.split() if word not in categorias_palabras_clave["Precio"]])
  cantidad = " ".join([word for word in cantidad.split() if word not in categorias_palabras_clave["Cantidad"]])
  comando = comando if comando else None
  nombre_producto = procesar_alias(nombre_producto)
  precio = return_price(precio)
  cantidad = return_cantidad(cantidad)

  resultado = {
        "texto": texto,
        "comando": comando,
        "nombre_producto": nombre_producto,
        "precio": precio,
        "cantidad": cantidad
   }

  return resultado


if __name__ == "__main__":
    ejemplo_texto = "agregar doce coca cola de novecientos mililitros salio un sol ochenta "
    recibirjson(ejemplo_texto)