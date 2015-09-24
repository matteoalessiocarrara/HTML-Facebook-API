# HTML Facebook API #

API non ufficiali basate sul codice HTML di Facebook

## Esempio ##

Stampa il nome di tutti i membri di un gruppo

```python
import htmlfbapi

email = ""
passw = ""
gid = "" #id del gruppo, una cosa come 1484239995227666 (per ora manca una funzione per elencare gli id, ma si vedono nell'url dal sito)

#connessione a fb
profilo1 = htmlfbapi.Facebook(email, passw)

#gruppo visto da profilo1
gruppo = profilo1.get_group(gid) 

profili = gruppo.members()

for profilo in profili:
	print profilo['name'].encode("utf8")
```

## Oggetti e metodi ##

Vedere con pydoc o leggere il sorgente, attualmente il login a fb funziona ma non ci sono molte altre cose

## Aggiornamenti ##

Questa libreria attualmente è incompleta, perché l'ho scritta solo per fare un software e quindi non mi serviva con più cose. Visto che è software free, se avete fatto delle modifiche che pensate potrebbero essere utili anche ad altri inviatemi un email, una pull request su GitHub o pubblicate voi le vostre modifiche (che io copierò xD).

## Altre informazioni ##

> This is the Unix philosophy: Write programs that do one thing and do it well. Write programs to work together. Write programs to handle text streams, because that is a universal interface.  

Aggiornamenti: [GitHub] (https://github.com/matteoalessiocarrara)  
Email: sw.matteoac@gmail.com
