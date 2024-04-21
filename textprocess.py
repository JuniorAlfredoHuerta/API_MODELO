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

comandos1 = ["agregar" , "buscar", "descargar", "actualizar","mostrar","vender","vendi","anadir","producto" ]
comandos2= ["inca kola", "coca cola", "fanta", "san luis", "galleta", "rellenita","san mateo", "cielo", "gaseosa", "galleta" ]
comandos3 = ["precio", "costo", "a", "salio"]
comandos4 = ["cantidad", "compre" , "recibi", "producto","salio"]
comandos5= ["litro", "mililitro","gramo","kilo","kilogramo", "soles", "centimos", "sol","de"]
comandos6 = ["docena", "decena", "centena", "media", "cuarto", "tercio"]


dictionary = w2n.NUMBER_WORDS + comandos1 + comandos2+comandos3+comandos4+comandos5+comandos6

def return_price(precio):
    if precio:
        precio_decimal = 0.0
        precio_tokens = precio.lower().split()
        for i in range(len(precio_tokens)):
            if precio_tokens[i] == "soles" or precio_tokens[i] == "sol" or precio_tokens[i] == "sols" or precio_tokens[i] == "solo":
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
    cantidad = correcion(cantidad, w2n.NUMBER_WORDS)
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

def correcion(texto, lista):
  textob = unidecode(texto)
  textoc = textob.split()
  corrected = []
  for i in range(len(textoc)):
    corregido = difflib.get_close_matches(textoc[i], lista, n=1, cutoff=0.6)
    if corregido:
      corrected.append(corregido[0])
    else:
      corrected.append(textoc[i])
  oracion_corregida = ' '.join(corrected)
  return oracion_corregida

def procesar_alias(descripcion):
  print(descripcion)
  if descripcion:
    tokens = descripcion.lower().split()
    numeroescr = []
    numero = 0
    totals = []
    nombreproducto = []
    real=[]
    for token in tokens:
        try:
            num = w2n.word_to_num(token)
            numeroescr.append(token)

        except ValueError:
            if token not in unidad_abreviacion:
              #token = token.capitalize()
              nombreproducto.append(token)
            elif( len(numeroescr) > 0):
              for i in range(len(numeroescr)):
                numeroescr[i] = w2n.word_to_num(numeroescr[i])
                numero += numeroescr[i]

              totals.append(numero)
              palabra_procesada = buscar_singular(token)

              totals.append(palabra_procesada)

            else:
                totals.append(token)
    print(nombreproducto)
    nombreproducto = " ".join(nombreproducto)
    print(nombreproducto)
    tokens = nombreproducto[0].lower().split()

    nombreproducto = difflib.get_close_matches(nombreproducto, comandos2, n=1,cutoff=0.6)
    print(nombreproducto)

    tokens = nombreproducto[0].lower().split()
    for token in tokens:
              token = token.capitalize()
              real.append(token)
    real.extend(totals)

    descripcion_procesada = " ".join([str(item) if isinstance(item, int) else item for item in real])
    return descripcion_procesada


def comandotoken(frase):
   frase = correcion(frase , comandos1)
   re = []
   if frase:
    tokens = frase.lower().split()

    return tokens[0]

def limpiar_texto(texto):
    texto_sin_tildes = unidecode(texto)
    texto_minusculas = texto_sin_tildes.lower()
    return texto_minusculas


categorias_palabras_clave = {
    "Comando": ["agregar" , "buscar", "desactivar", "actualizar","mostrar","vender","vendi","anadir","producto","descargar","enviar" ]   ,
    "Producto": ["inca", "coca","fanta", "san", "galleta", "rellenita","san", "agua", "gaseosa", "galleta","agua", "cielo","incacola"],
    "Precio": ["precio", "costo", "a", "salio"],
    "Cantidad": ["cantidad", "compre" , "recibi", "vendi"]
}

def checkcomando( pre, a, doc, filtros):
  word1 = ""
  print(len(doc))
  for l in range(a+1):
    if pre + l < len(doc):
      word1 += doc[pre + l]
  word = correcion(word1, filtros)
  print(word)
  print(word , a)
  if len(doc) >= a:
    if word in filtros:
      return word , a
    else:
      return checkcomando(pre, a + 1, doc, filtros)
  else:
    return "", 0


def recibirjson(texto):

  texto = limpiar_texto(texto)


  doc2 = texto.split()
  doc3 = texto.split()
  docfinal = " "
      #print("----------------------", doc2[i], "------------------")
      #print("Comandos 1", correcion(doc2[i], comandos1))
      #print("Comandos 2", correcion(doc2[i], comandos2))
      #print("Comandos 3", correcion(doc2[i], comandos3))
      #print("Comandos 4", correcion(doc2[i], comandos4))
      #print("Comandos 5", correcion(doc2[i], comandos5))
      #print("Comandos 6", correcion(doc2[i], comandos6))
      #print("numeros", correcion(doc2[i],w2n.NUMBER_WORDS))
      #print(i , doc2[i])
  pre = 0
  posi = 0
  for i in range(8):
    pos=0
    if i == 0:
      comandos = comandos1+comandos4
    elif i == 1:
      comandos = w2n.NUMBER_WORDS+comandos6
    elif i == 2:
      comandos = comandos2
    elif i == 3:
      comandos = comandos3
    elif i == 4:
      comandos = w2n.NUMBER_WORDS
    elif i == 5:
      comandos = comandos5
    elif i == 6:
      comandos = w2n.NUMBER_WORDS
    elif i == 7:
      comandos = comandos5


    newcomando , pos= checkcomando(pre, pos, doc3, comandos)
    doc3[pos] = newcomando
    del doc3[:pos]

    posi += pos +1


    pre += 1
    docfinal += newcomando + " "
    if posi == len(doc2):
      break
        #print(doc2[i])
        #print(doc2[i+1])
#
        #print("Comandos 1", correcion(doc2[i], comandos1+comandos4))
        #a = correcion(doc2[i], comandos1)
        #if a in comandos1+comandos4:
        #  print("a la primera")
        #  print(a)
        #else:
        #  print("segunda")
        #  word = doc2[i]+doc2[i+1]
        #  print(word)
        #  print("Comandos 1", correcion(word, comandos1+comandos4))






  print(texto)
  print(docfinal)
  comando = ""
  nombre_producto = ""
  precio = ""
  cantidad = ""
  current_key = None
  doc = nlp(docfinal)

  for token in doc:

      token_text = token.text.lower()
      token_text = comandotoken(token_text)

      for categoria, palabras_clave in categorias_palabras_clave.items():
          if token_text in palabras_clave:
              current_key = categoria
              break

      if current_key:
          if current_key == "Comando":
              comando += " " + token.text
              cantidad += " " + token.text
          elif current_key == "Producto":
              nombre_producto += " " + token.text
          elif current_key == "Precio":
              precio += " " + token.text
          elif current_key == "Cantidad":
              cantidad += " " + token.text


  #nombre_producto = " ".join([word for word in nombre_producto.split() if word not in categorias_palabras_clave["Producto"]])
  precio = " ".join([word for word in precio.split() if word not in categorias_palabras_clave["Precio"]])
  #print(precio)
  cantidad = " ".join([word for word in cantidad.split() if word not in categorias_palabras_clave["Cantidad"]])
  #print(cantidad)

  comando = comandotoken(comando)
  #print(comando)

  nombre_producto = procesar_alias(nombre_producto)
  #print(nombre_producto)

  precio = return_price(precio)
  #print(precio)

  cantidad = return_cantidad(cantidad)
  #print(cantidad)
  resultado = {
        "texto": texto,
        "comando": comando,
        "nombre_producto": nombre_producto,
        "precio": precio,
        "cantidad": cantidad
   }
  print(resultado)

  return resultado

if __name__ == "__main__":
    ejemplo_texto = "ve der cin co"
    recibirjson(ejemplo_texto)