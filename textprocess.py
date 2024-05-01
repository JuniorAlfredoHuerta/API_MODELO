import spacy
from word2number_es import w2n
import re
import json
from unidecode import unidecode
import difflib
from spellchecker import SpellChecker
stop_words = set(spacy.lang.es.STOP_WORDS)
spell = SpellChecker(language='es')

comandos1 = ["agregar" , "buscar", "descargar", "actualizar","mostrar","vender","vendi","anadir" ]
comandos2= ["inca kola", "coca cola", "fanta", "san luis", "galleta", "rellenita","san mateo", "cielo", "gaseosa", "galleta" ]
comandos3 = ["precio", "costo", "a", "salio", "total"]
comandos4 = ["cantidad", "compre" , "recibi"]
comandos5= ["litro", "mililitro","gramo","kilo","kilogramo", "soles", "centimos", "sol","de"]
comandos6 = ["docena", "decena", "centena", "media", "cuarto", "tercio"]
comandos7= ["producto", "nombre"]


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

        doc = " ".join([token for token in tokens_not_recog if token not in stop_words])
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
    corregido = difflib.get_close_matches(textoc[i], lista, n=1, cutoff=0.7)
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
    "Precio": ["precio", "costo", "a", "salio", "total"],
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


def corregir(word, wordnew, lista, texto, i):
    index = texto.index(word)
    #print("posi", index, i)
    posi = [index, i]

    if index != i:
        #print("AQUI")
        wordnew = texto[posi[0]:posi[1]+1]
        wordnew = "".join(wordnew)
        #print("this is the word",wordnew)
    else:
        wordnew = word

    tamanio = len(texto)
    palabra = difflib.get_close_matches(wordnew, lista, n=1, cutoff=0.7)
    if len(palabra) != 0:
        palabra = palabra[0]
        #print(palabra)
        if palabra in lista and palabra is not None:
            #print("se logro")
            #print(palabra,i)
            return palabra , i
    else:
        #print("here we go")
        if i < tamanio:
            #print("again")
            return corregir(word, wordnew, lista, texto, i+1)
        else:
            return "",i


def recibirjson(texto):

    texto = limpiar_texto(texto)
    palabras = texto.split()

    comando = None
    cantidad = None
    nombre_producto = None
    precio = None

    i = 0
    cpoint = -1
    npoint = -1
    ppoint = -1

    filtros1 = comandos1+comandos4
    filtros2 = comandos7
    filtros3 = comandos3


    while i < len(palabras):
        if corregir(palabras[i], palabras[i], filtros1,palabras,i)[0] in filtros1 and cpoint == -1:
            a , b =   corregir(palabras[i], palabras[i], filtros1,palabras,i)
            comando = a
            i = b
            cpoint = i
        elif corregir(palabras[i], palabras[i], filtros2,texto,i)[0] in filtros2 and npoint == -1:
            a , b =   corregir(palabras[i], palabras[i], filtros2,palabras,i)
            i = b
            npoint = i
        elif corregir(palabras[i], palabras[i], filtros3,texto,i)[0] in filtros3 and ppoint == -1:
            a , b =   corregir(palabras[i], palabras[i], filtros3, palabras,i)
            i = b
            ppoint = i
        else:
            i += 1

    if cpoint != -1 and npoint != -1:
        cantidad_words = palabras[cpoint+1:npoint]
        cantidad = ' '.join(cantidad_words)
        cantidad = return_cantidad(cantidad)

    if npoint != -1 and ppoint != -1:
        nombre_words = palabras[npoint+1:ppoint]
        nombre_producto = ' '.join(nombre_words)
        nombre_producto = difflib.get_close_matches(nombre_producto, comandos2, n=1, cutoff=0.7)[0]
        nombre_producto = procesar_alias(nombre_producto)
    if ppoint != -1:
        precio_words = palabras[ppoint+1:]
        precio = ' '.join(precio_words)
        precio = return_price(precio) 

    resultado = {
          "texto": texto,
          "comando": comando,
          "nombre_producto": nombre_producto,
          "precio": precio,
          "cantidad": cantidad
     }

    return resultado
if __name__ == "__main__":
    ejemplo_texto = "añ adir dioeciocho nombre cinca ca cola salio cincuenta soles  ochenta"
    recibirjson(ejemplo_texto)

if __name__ == "__main__":
    ejemplo_texto = "ve der cin co"
    recibirjson(ejemplo_texto)