# script-quitar-acordes
Script en python para quitar acordes de guitarra de varios archivos de texto que estén en una carpeta

**REQUERIMIENTOS**
python

**USO**
EL programa no tiene insterfaz gráfica, solo se usa desde terminal así:

```
python3 remove_chords.py
```

y automáticamente todo lo que está en la carpeta:

canciones-a-quitar-acordes

se copiará a la carpeta:

canciones-quitadas-acordes

pero sin acordes.

**PROBADO EN:**
Debian 12

El siguiente es un ejemplo de lo que hace este script, tengo un archivo de texto en la carpeta:

canciones-a-quitar-acordes/La niña de tus ojos - Daniel Calveti (B).txt

este archivo tiene el siguiente contenido:

```
La niña de tus ojos
Daniel Calveti
B F# Abm E
B F# Abm E

VERSO I X2
         B                  F#
Me viste a mi cuando nadie me vio
          Abm                E
Me amaste a mi cuando nadie me amo

VERSO II X2
            B                F#
Y me diste nombre yo soy tu niña
               Abm                    E
La niña de tus ojos por que me amaste a mí

PRE-CORO X2
          B               F#
Me amaste a mí, Me amaste a mí,
          Abm             E
Me amaste a mí, Me amaste a mí

CORO X 4
B                        F#
Te amo más que a mi vida,
                         Abm
te amo más que a mi vida,
                           E
Te amo más que a mi vida, más

VERSO II X2
            B                F#
Y me diste nombre yo soy tu niña
               Abm                    E
La niña de tus ojos por que me amaste a mí

          B
Me amaste a mí.
```
y al abrir una terminal aquí en este repositorio y poner:

```
python3 remove_chords.py 
```

así como se ve en al siguiente imagen:

![](vx_images/11653823289001.png)

el resultado lo pone en la carpeta:

canciones-quitadas-acordes/

lo deja así:


```
La niña de tus ojos
Daniel Calveti

VERSO I X2
Me viste a mi cuando nadie me vio
Me amaste a mi cuando nadie me amo

VERSO II X2
Y me diste nombre yo soy tu niña
La niña de tus ojos por que me amaste a mí

PRE-CORO X2
Me amaste a mí, Me amaste a mí,
Me amaste a mí, Me amaste a mí

CORO X 4
Te amo más que a mi vida,
te amo más que a mi vida,
Te amo más que a mi vida, más

VERSO II X2
Y me diste nombre yo soy tu niña
La niña de tus ojos por que me amaste a mí

Me amaste a mí.
```

lo mismo hace con todos los archivos de texto que estén en:

canciones-a-quitar-acordes/
