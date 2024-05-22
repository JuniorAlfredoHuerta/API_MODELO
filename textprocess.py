import spacy
from word2number_es import w2n
import re
import json
from unidecode import unidecode
import difflib
from spellchecker import SpellChecker
from num2words import num2words

stop_words = {'podriais', 'ninguno', 'ésta', 'alli', 'nuestras', 'hubo', 'alguna', 'decir', 'conseguir', 'propias', 'diferentes', 'cual', 'podrias', 'te', 'próximo', 'estar', 'ambos', 'mia', 'míos', 'consigo', 'despacio', 'manifestó', 'poca', 'saber', 'serán', 'estan', 'porque', 'tienen', 'supuesto', 'vuestros', 'mías', 'aun', 'cuatro', 'existe', 'quién', 'usamos', 'ellas', 'ése', 'despues', 'trata', 'también', 'usas', 'siempre', 'una', 'cuantas', 'segun', 'largo', 'diez', 'donde', 'teneis', 'adelante', 'quiénes', 'consideró', 'aquéllas', 'nueve', 'lleva', 'esta', 'buen', 'éstos', 'temprano', 'podrán', 'ciertas', 'debido', 'unos', 'eran', 'u', 'tu', 'por', 'muchos', 'tuyas', 'bien', 'consigues', 'hicieron', 'quizas', 'nuestro', 'tres', 'peor', 'habia', 'mío', 'vuestras', 'pueden', 'ningunas', 'ha', 'no', 'llegó', 'cuantos', 'él', 'las', 'usa', 'tuyos', 'solamente', 'aquellas', 'haya', 'propio', 'habrá', 'habían', 'mejor', 'sino', 'tanto', 'ello', 'usted', 'ninguna', 'fuera', 'estas', 'algunas', 'partir', 'dia', 'uso', 'aquello', 'creo', 'nos', 'cuenta', 'hacerlo', 'tuyo', 'estuvo', 'mucha', 'aunque', 'fueron', 'haces', 'esas', 'cualquier', 'tarde', 'mencionó', 'suyo', 'propia', 'sois', 'ella', 'primeros', 'vaya', 'sabeis', 'se', 'doce', 'hecho', 'del', 'hablan', 'solo', 'nuevas', 'varias', 'cuándo', 'mis', 'realizado', 'podrá', 'sería', 'durante', 'encuentra', 'de', 'cuanta', 'ir', 'son', 'añadió', 'ningunos', 'pues', 'que', 'tenido', 'acuerdo', 'considera', 'otro', 'aquél', 'suyas', 'consigue', 'qeu', 'ver', 'suyos', 'les', 'mal', 'ultimo', 'aquéllos', 'ahi', 'ahora', 'está', 'haber', 'menudo', 'todas', 'verdadera', 'aquélla', 'dias', 'mí', 'delante', 'pasado', 'vamos', 'aseguró', 'última', 'tal', 'arriba', 'éste', 'la', 'tener', 'pero', 'quizás', 'paìs', 'salvo', 'aquellos', 'aún', 'apenas', 'mientras', 'pocos', 'nunca', 'todavía', 'agregó', 'tercero', 'bastante', 'nuestros', 'ademas', 'seis', 'sin', 'últimos', 'sé', 'sí', 'ellos', 'éstas', 'claro', 'consiguen', 'algún', 'ni', 'algunos', 'enseguida', 'repente', 'en', 'tan', 'nueva', 'conmigo', 'sigue', 'final', 'al', 'nosotros', 'podriamos', 'he', 'yo', 'deprisa', 'quizá', 'conseguimos', 'ese', 'le', 'través', 'mias', 'sido', 'todavia', 'como', 'cuando', 'hacer', 'uno', 'dado', 'tendrá', 'si', 'dejó', 'sean', 'más', 'unas', 'nadie', 'vuestra', 'haciendo', 'conocer', 'sobre', 'dos', 'explicó', 'tenga', 'esos', 'primero', 'atras', 'sus', 'todos', 'bueno', 'siguiente', 'grande', 'igual', 'asi', 'indicó', 'somos', 'nosotras', 'parte', 'quiza', 'están', 'dar', 'vosotros', 'es', 'primer', 'hemos', 'menos', 'parece', 'embargo', 'aqui', 'segunda', 'ya', 'queremos', 'luego', 'poner', 'van', 'usan', 'buenos', 'saben', 'afirmó', 'mucho', 'hago', 'o', 'nuevo', 'e', 'contigo', 'este', 'tampoco', 'gran', 'un', 'mi', 'hizo', 'muchas', 'vais', 'solos', 'fuimos', 'mayor', 'tiene', 'dijo', 'esa', 'pocas', 'con', 'otras', 'hasta', 'allí', 'cinco', 'detras', 'os', 'cuántas', 'realizó', 'me', 'soy', 'quienes', 'cierta', 'informó', 'eso', 'han', 'nuevos', 'mios', 'aquella', 'ésas', 'tercera', 'demasiado', 'tuya', 'sabe', 'solas', 'sola', 'verdadero', 'cuanto', 'esto', 'dio', 'incluso', 'señaló', 'según', 'lo', 'mismas', 'últimas', 'siete', 'hacemos', 'tú', 'cierto', 'realizar', 'dicho', 'dónde', 'varios', 'estará', 'podria', 'ésa', 'da', 'días', 'alrededor', 'cuántos', 'mía', 'veces', 'propios', 'tus', 'entre', 'hacia', 'el', 'otra', 'ningún', 'dieron', 'nuestra', 'y', 'dan', 'bajo', 'segundo', 'quien', 'sera', 'anterior', 'modo', 'mediante', 'así', 'demás', 'nada', 'hace', 'cada', 'tendrán', 'los', 'muy', 'haceis', 'proximo', 'voy', 'pesar', 'detrás', 'mas', 'diferente', 'quedó', 'próximos', 'total', 'vez', 'sea', 'todo', 'último', 'debe', 'estos', 'desde', 'mismo', 'excepto', 'puedo', 'vuestro', 'breve', 'hay', 'estoy', 'había', 'dice', 'fin', 'estaba', 'ciertos', 'eras', 'tenemos', 'usais', 'era', 'lado', 'su', 'hacen', 'aproximadamente', 'estado', 'primera', 'cómo', 'poder', 'pronto', 'va', 'mio', 'dicen', 'aquí', 'cuál', 'poco', 'dijeron', 'estados', 'será', 'cuánta', 'contra', 'suya', 'podeis', 'pudo', 'grandes', 'sabes', 'sólo', 'eramos', 'medio', 'once', 'posible', 'antes', 'qué', 'manera', 'pueda', 'ti', 'podemos', 'usar', 'ante', 'tambien', 'puede', 'podría', 'además', 'ocho', 'pasada', 'habla', 'tuvo', 'respecto', 'tenía', 'después', 'expresó', 'encima', 'vosotras', 'eres', 'estamos', 'a', 'fui', 'junto', 'sabemos', 'ser', 'alguno', 'tengo', 'hoy', 'ahí', 'toda', 'llevar', 'podrían', 'casi', 'para', 'podrian', 'deben', 'estaban', 'misma', 'cuánto', 'enfrente', 'algo', 'aquel', 'comentó', 'debajo', 'otros', 'estais', 'buenas', 'día', 'tras', 'buena', 'existen', 'mismos', 'cuáles', 'dentro', 'fue', 'ésos', 'quiere', 'siendo', 'verdad', 'informo', 'ustedes', 'entonces', 'cuales'}
spell = SpellChecker(language='es')

comandos1 = ["agregar" , "buscar", "descargar", "actualizar","mostrar","vender","vendi","anadir" ]
comandos2= ["inca kola", "coca cola", "fanta", "san luis", "galleta", "rellenita","san mateo", "cielo", "gaseosa", "galleta" ]
comandos3 = ["precio", "costo", "a", "salio", "total"]
comandos4 = ["cantidad", "compre" , "recibi"]
comandos5= ["litro", "mililitro","gramo","kilo","kilogramo"]
comandos6 = ["docena", "decena", "centena", "media", "cuarto", "tercio"]
comandos7= ["producto", "nombre"]
comandos8 = [ "soles", "centimos", "sol"]
correcunidades = ['cero',
 'uno',
 'dos',
 'tres',
 'cuatro',
 'cinco',
 'seis',
 'siete',
 'ocho',
 'nueve',
 'diez']
correcentenas = ['cien',
 'ciento',
 'doscientos',
 'trescientos',
 'cuatrocientos',
 'quinientos',
 'seiscientos',
 'setecientos',
 'ochocientos',
 'novecientos']
correcdecenas = [
     'diez',
 'once',
 'doce',
 'trece',
 'catorce',
 'quince',
 'dieciseis',
 'diecisiete',
 'dieciocho',
 'diecinueve',
 'veinte',
 'veintiuno',
 'veintiun',
 'veintidos',
 'veintitres',
 'veinticuatro',
 'veinticinco',
 'veintiseis',
 'veintisiete',
 'veintiocho',
 'veintinueve',
 'treinta',
 'cuarenta',
 'cincuenta',
 'sesenta',
 'setenta',
 'ochenta',
 'noventa'
 ]


dictionary = w2n.NUMBER_WORDS + comandos1 + comandos2+comandos3+comandos4+comandos5+comandos6

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

def limpiar_texto(texto):
    texto_sin_tildes = unidecode(texto)
    texto_minusculas = texto_sin_tildes.lower()
    return texto_minusculas
def capitalizar_primera_letra(cadena, unidad_abreviacion):
    palabras = cadena.split()
    nueva_cadena = []

    for palabra in palabras:
        if palabra.lower() in unidad_abreviacion.values():
            nueva_cadena.append(palabra)
        else:
            nueva_cadena.append(palabra.capitalize())
    return ' '.join(nueva_cadena)



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

def corregirnumero(texto):
  total = 0

  texto = texto.replace(" y ", " ")
  texto = texto.replace(" i ", " ")
  texto = texto.split()
  if "docena" in texto:
    i = texto.index("docena")
    pre = texto[:i]
    pre = " ".join(pre)
    if pre == "una":
      pre = 1
    else:
      pre = corregirnumero(pre)
    total = pre * 12
  elif "docenas" in texto :
    i = texto.index("docenas")
    pre = texto[:i]
    pre = " ".join(pre)
    if pre == "una":
      pre = 1
    else:
      pre = corregirnumero(pre)
    total = pre * 12
  else:
    i = 0
    centena = 0
    decena = 0
    unidad = 0
    centena, pos =   hallar(i,i , texto, correcentenas)
    #print(centena, pos)
    if i < len(texto) and decena == 0:
      if centena != 0:
       i = pos +1
      decena, pos =   hallar(i,i , texto, correcdecenas)
      #print(decena, pos)

    if i < len(texto) and unidad == 0:
      if decena != 0:
       i = pos +1
      unidad, pos =   hallar(i,i , texto, correcunidades)
      #print(unidad, pos)
    total = centena + decena + unidad
  return total

def hallar( pre , pos, texto, lista):
  word = ""
  if pos >= len(texto):
    return 0, pre
  if pre == pos:
    word = texto[pre]
  elif pos <= len(texto):
    word = " ".join(texto[pre:pos+1])

  if len(difflib.get_close_matches(word, lista, n=1, cutoff=0.8)) > 0:
    numero = difflib.get_close_matches(word, lista, n=1, cutoff=0.8)[0]
    numero = w2n.word_to_num(numero)
    return numero , pos
  elif pos < len(texto):
    return hallar(pre, pos +1 , texto, lista)
  else:
    return 0 , pre

def return_price(texto):
  texto= limpiar_texto(texto)
  palabras = texto.split()
  i = 0
  puntomedio = -1
  unidad = 0
  centimos = 0
  while i < len(palabras):
    if difflib.get_close_matches(palabras[i], ["soles"], n=1, cutoff=0.7) and puntomedio == -1:
      unidad = palabras[:i]
      centimos  = palabras[i+1:]
      unidad = " ".join(unidad)
      centimos = " ".join(centimos)
      unidad = corregirnumero(unidad)
      centimos = corregirnumero(centimos)
      i += 1
    else:
      i += 1
  return   unidad + (centimos/100)

def convertir_numeros_a_texto_en_cadena(cadena):
    patron_numeros = re.compile(r'\b\d+(\.\d+)?\b')

    def reemplazar_numeros(match):
        numero = match.group(0)
        if '.' in numero:
            numero = float(numero)
        else:
            numero = int(numero)
        return str(num2words(numero, lang='es'))

    cadena_convertida = patron_numeros.sub(reemplazar_numeros, cadena)

    return cadena_convertida

def procesar_alias(texto):
  texto= limpiar_texto(texto)
  palabras = texto.split()
  i = 0
  puntomedio = -1
  numero  = -1
  nombrec = -1
  npoint = -1
  mediciopoint = -1
  pre = None
  pos = None
  cantidad = None
  unidad = None
  while i < len(palabras):
      if difflib.get_close_matches(palabras[i], ["de"], n=1, cutoff=0.7) and puntomedio == -1:
        puntomedio = i
        pre = palabras[:i]
        pre = " ".join(pre)
        pre = difflib.get_close_matches(pre, comandos2, n=1, cutoff=0.7)[0]
        pre = pre.capitalize()
        pos = palabras[i+1:]
        i += 1
      elif difflib.get_close_matches(palabras[i], w2n.NUMBER_WORDS, n=1, cutoff=0.7) and npoint == -1:
        print("numero" ,palabras[i])
        npoint = i
        i += 1
      elif difflib.get_close_matches(palabras[i], comandos5, n=1, cutoff=0.7)  and mediciopoint == -1:
        mediciopoint = i
        print("medicion", palabras[i])
        i += 1
      else:
        i += 1
  if puntomedio == -1:
    pre = difflib.get_close_matches(texto, comandos2, n=1, cutoff=0.7)[0]
    return pre
  if npoint != -1:
      if mediciopoint == -1:
        cantidad = palabras[puntomedio+1:]
      else:
        cantidad = palabras[puntomedio+1:mediciopoint]
        unidad = palabras[mediciopoint:]
        unidad = " ".join(unidad)
        unidad = buscar_singular(unidad)
        cantidad = " ".join(cantidad)
        cantidad = corregirnumero(cantidad)
  return pre + " " + str(cantidad) + " " + unidad

unidad_abreviacion = {
    "litro": "L",
    "mililitro": "ml",
    "gramo": "g",
    "kilo": "kg",
    "kilogramo": "kg",
}

unidadcontra = {
    "L": "litro",
    "ml": "mililitro",
    "g": "gramo",
    "kg": "kilo",
    "l": "litro",
    "ML": "mililitro",
    "G": "gramo",
    "KG": "kilo",
    "Ml": "mililitro",
    "Kg": "kilo",
    "mL": "mililitro",
    "kG": "kilo",
}

frases_especiales = {
    "medio litro": "500 mL",
    "personal": "500 mL",
}
def convertir_abreviaciones_a_unidades(texto, unidad_abreviacion):
    regex = re.compile(r'\b(' + '|'.join(re.escape(abrv) for abrv in unidad_abreviacion.keys()) + r')\b')

    def reemplazo(match):
        return unidad_abreviacion[match.group(0)]

    nuevo_texto = regex.sub(reemplazo, texto)

    return nuevo_texto


def buscar_singular(palabra):
    palabra = difflib.get_close_matches(palabra, comandos5, n=1, cutoff=0.7)[0]
    palabra_singular = unidad_abreviacion.get(palabra, palabra)
    return palabra_singular

def procesar_frase_especial(frase):
    return frases_especiales.get(frase, frase)

def numero_a_palabras(numero):
    parte_entera, _, parte_decimal = str(numero).partition('.')
    parte_entera = int(parte_entera)
    parte_decimal = int(parte_decimal) if parte_decimal else 0

    palabras_entero = num2words(parte_entera, lang='es')
    
    if parte_entera == 1:
        palabras_entero += " sol"
    else:
        palabras_entero += " soles"

    if parte_decimal > 0:
        palabras_decimal = num2words(parte_decimal*10, lang='es')
        resultado = f"{palabras_entero} {palabras_decimal}"
    else:
        resultado = palabras_entero
    
    return resultado  

def recibirjson(texto):
    texto = convertir_numeros_a_texto_en_cadena(texto)
    texto = convertir_abreviaciones_a_unidades(texto, unidadcontra)
    texto = limpiar_texto(texto)
    palabras = texto.split()
    nuevo_texto = []

    comando = None
    cantidad = None
    nombre_producto = None
    precio = None
    palabraproducto = None
    palabraprecio = None

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
            palabraproducto = a
            npoint = i
        elif corregir(palabras[i], palabras[i], filtros3,texto,i)[0] in filtros3 and ppoint == -1:
            a , b =   corregir(palabras[i], palabras[i], filtros3, palabras,i)
            i = b
            palabraprecio = a
            ppoint = i
        else:
            i += 1
    #print(cpoint,npoint,ppoint)
    if cpoint != -1:
      if npoint == -1:
        cantidad_words = palabras[cpoint+1:]
      else:
        cantidad_words = palabras[cpoint+1:npoint]

      cantidad = ' '.join(cantidad_words)
      cantidad = corregirnumero(cantidad)




      #cantidad = return_cantidad(cantidad)
    if npoint != -1:
        if ppoint == -1:
          nombre_words = palabras[npoint+1:]
        else:
          nombre_words = palabras[npoint+1:ppoint]
        nombre_producto = ' '.join(nombre_words)
       #nombre_producto = difflib.get_close_matches(nombre_producto, comandos2, n=1, cutoff=0.7)[0]
        nombre_producto = procesar_alias(nombre_producto)
    if ppoint != -1:
        precio_words = palabras[ppoint+1:]
        precio = ' '.join(precio_words)
        precio = return_price(precio)

    if nombre_producto != None:
      nombre_producto = capitalizar_primera_letra(nombre_producto,unidad_abreviacion);

    #nuevo_texto.append(comando)
    #nuevo_texto.append(num2words(cantidad, lang='es'))
    #nuevo_texto.append(palabraproducto)
    #nuevo_texto.append(nombre_producto.lower())
    #nuevo_texto.append(palabraprecio)
    #nuevo_texto.append(numero_a_palabras(precio))

    if comando is not None:
        nuevo_texto.append(comando)
    if cantidad != 0:
        nuevo_texto.append(num2words(cantidad, lang='es')) 
    if palabraproducto is not None:
        nuevo_texto.append(palabraproducto) 
    if nombre_producto is not None:
        nuevo_texto.append(nombre_producto.lower())
    if palabraprecio is not None:
        nuevo_texto.append(palabraprecio)
    if precio is not None:
        nuevo_texto.append(numero_a_palabras(precio))

    nuevo_texto = ' '.join(nuevo_texto)
    resultado = {
          "texto": texto,
          "comando": comando,
          "nombre_producto": nombre_producto,
          "precio": precio,
          "cantidad": cantidad
     }
    return resultado , nuevo_texto
if __name__ == "__main__":
    ejemplo_texto = "agregar diez producto in ca col cost tres soles cincuenta"

    print(recibirjson(ejemplo_texto))