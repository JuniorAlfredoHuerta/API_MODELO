import spacy
from word2number_es import w2n
import re
import json
nlp = spacy.load("es_core_news_sm")
stop_words = set(spacy.lang.es.STOP_WORDS)


def return_price(precio):
    if precio:
        precio_decimal = 0.0
        precio_tokens = precio.lower().split()
        for i in range(len(precio_tokens)):
            if precio_tokens[i] == "soles" or precio_tokens[i] == "sol" or precio_tokens[i] == "solo":
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
    "litros": "L",
    "mililitro": "mL",
    "mililitros": "mL",
    "gramo": "g",
    "gramos": "g",
    "kilo": "kg",
    "kilos": "kg",
    "kilogramo": "kg",
    "kilogramos": "kg",
}

diccionario_palabras = w2n.NUMBERS

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
    "medio docena": lambda numero: numero * 6,
    "docena medio": lambda numero: numero * 12 + 6,
    "docena": lambda numero: numero * 12,
    "decena": lambda numero: numero * 10,
    "decena media": lambda numero: numero * 10 + 5,
    "medio decena": lambda numero: numero * 5,
    "cuarto": lambda numero: numero * 3,
    "tercio": lambda numero: numero * 4,
    "medio centena": lambda numero: numero * 50,
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

def corregir_numero(frase):
    # Utiliza una expresión regular para buscar "una" o "un" como palabras completas en la frase
    frase_corregida = re.sub(r'\buna\b', 'uno', frase, flags=re.IGNORECASE)
    frase_corregida = re.sub(r'\bun\b', 'uno', frase_corregida, flags=re.IGNORECASE)
    return frase_corregida


categorias_palabras_clave = {
    "Agregar": ["agregar"],
    "Buscar": ["buscar"],
    "Desactivar": ["desactivar"],
    "Actualizar": ["actualizar"],
    "Mostrar": ["mostrar"],
    "Vender": ["vender"],    
    "Producto": ["inca", "coca", "fanta", "san", "galleta", "rellenita","san", "agua", "gaseosa", "galleta"],
    "Precio": ["precio", "costo", "a", "salio"],
    "Cantidad": ["cantidad", "compre" , "recibi"]
}

def recibirjson(texto):

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
          if current_key == "Agregar":
              comando += " " + token.text
              cantidad += " " + token.text
          elif current_key == "Buscar":
              comando += " " + token.text
          elif current_key == "Desactivar":
              comando += " " + token.text
          elif current_key == "Actualizar":
              comando += " " + token.text
          elif current_key == "Mostrar":
              comando += " " + token.text
          elif current_key == "Vender":
              comando += " " + token.text
          elif current_key == "Producto":
              nombre_producto += " " + token.text
          elif current_key == "Precio":
              precio += " " + token.text
          elif current_key == "Cantidad":
              cantidad += " " + token.text


  #nombre_producto = " ".join([word for word in nombre_producto.split() if word not in categorias_palabras_clave["Producto"]])
  precio = " ".join([word for word in precio.split() if word not in categorias_palabras_clave["Precio"]])
  cantidad = " ".join([word for word in cantidad.split() if word not in categorias_palabras_clave["Cantidad"]])
  precio = corregir_numero(precio)
  cantidad = corregir_numero(cantidad)
  comando = comando.strip() if comando else None
  nombre_producto = procesar_alias(nombre_producto)
  precio = return_price(precio)
  cantidad = return_cantidad(cantidad)

  resultado = {
        "comando": comando,
        "nombre_producto": nombre_producto,
        "precio": precio,
        "cantidad": cantidad
   }

  return resultado


if __name__ == "__main__":
    ejemplo_texto = "agregar doce coca cola de novecientos mililitros salio un sol ochenta "
    recibirjson(ejemplo_texto)