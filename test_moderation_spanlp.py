from spanlp.palabrota import Palabrota

palabrota = Palabrota()
palabra = "hola pendejo"


print("-------Censura Default y Booleano------------")

print("Palabrota: ", palabra)
print(palabrota.censor(palabra))
print("Palabrota: ", palabra)
print(palabrota.contains_palabrota(palabra))


print("-------Censura con Caracteres Especificos------------")

print("Palabrota: ", palabra)
palabrota._censor_chars = "x"
print(palabrota.censor(palabra))


print("--------Censura para pais Especifico-----------")

from spanlp.domain.countries import Country
palabrota = Palabrota(censor_char="@", countries=[Country.VENEZUELA])
print( "Venezuela: ", "Hola marico, cómo estás chucha?")
print(palabrota.censor("Hola marico, cómo estás chucha?"))
palabrota = Palabrota(censor_char="@", countries=[Country.VENEZUELA, Country.ECUADOR])
print( "Venezuela y Ecuador: ", "Hola marico, cómo estás chucha?")
print(palabrota.censor("Hola marico, cómo estás chucha?"))


print("--------Censura palabras similares-----------")

from spanlp.palabrota import Palabrota
from spanlp.domain.strategies import CosineSimilarity, TextToLower

palabrota = Palabrota(censor_char="*", distance_metric=CosineSimilarity())
print(palabrota.censor("Hola huevo maric cómo está, cara de la vrgá?"))


print("-------------------")

from spanlp.domain.strategies import Preprocessing, TextToLower, RemoveUnicodeCharacters, NumbersToVowelsInLowerCase, NumbersToConsonantsInLowerCase
strategies = [TextToLower(), RemoveUnicodeCharacters(), NumbersToVowelsInLowerCase(), NumbersToConsonantsInLowerCase()]
tweet = "Ho1a qu3 tªl, et°nc3s c0mo v4s @jhon, s1 v1ste que @freddy v4 a l4nzar una nu3v4 1ibreria Python?"
cleaned = Preprocessing().clean(data=tweet, clean_strategies=strategies)
print(cleaned)
print(palabrota.contains_palabrota(cleaned))


# Orden de Filtros:
# - TextToLower
# - RemoveUnicodeCharacters
# - NumbersToVowelsInLowerCase
# - NumbersToConsonantsInLowerCase