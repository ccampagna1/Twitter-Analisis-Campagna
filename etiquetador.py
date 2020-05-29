# -*- coding: utf-8 -*-
"""
Created on Thu May 14 22:07:14 2020

@author: Guido Pacella
"""
### Base dummy... lo que sea que se haga aguas arriba tiene que traer una lista de tuits. 
tuits = ['Primer comentario tiene hasta sesenta menos de caracteres', 'el segundo es puto', 
         'el tercero es un choclo de esos bien LARGOS Y LLENOS DE MAYUSCULAS QUE TE DAN PAJA LEER',
         'y terminamoas cin ub cuarto masl escrito porque ya nada sñgjasdgñ ñwegkj wdgkjv '
         'Ahora metemos otros comentarios más',
         'solo para mostrar como quedaría esto andando']

def green(s):
    return '\033[1;32m%s\033[m' % s


def yellow(s):
    return '\033[1;33m%s\033[m' % s


def red(s):
    return '\033[1;31m%s\033[m' % s

botones = yellow('\n\nPositivo -P-\tNegativo -N-\tNeutro -O-\t Revisar -R-\t Salir -S-\n')
instruc = green('\nRankear el siguiente tuit:\n\n')
instruc2 = green('\nRankear el siguiente tuit') + yellow(' (revisión):\n\n')
nova = red('\nERROR: Comando no válido\n')

proc = [] 
hechos = []
revisar = []

def iniciar():
    """Inicia a trabajar una lista de tuits. Carga la listia e inicializa las
    vacías las listas proc, hechos y revisar"""
    # no implementado aún
    pass

def resetear():
    """Resetear la sesión actual: mantiene tuits, pero elimina proc, hechos y 
    revisar en las variables de la consola"""
    # no implementado aún
    pass

def cargar():
    """Retoma un archivo guardado: lista de tuits original, y los indices
    de los tuits hechos, para reivión, y las procesados con sus etiquetas."""
    # no implementado aún
    pass

def guardar():
    """Exporta las listas proc, hechos y revisar, así como los tuits originales."""
    # no implementado aún
    pass

def rankear(tuits, proc = proc, hechos = hechos, revisar = revisar):
    """
    Crear etiquetas para los tuits no clasificados.
    Parámetros
    ----------
    tuits : lista de tuits, strings
    proc : tupla
        (tuit, ranking)         
    hechos : lista
        de indices (int) de la lista de tuits que ya están rankeados
    revisar : lista
        de indices (int) de la lista de tuits que quedaron para revisar

    Salida
    -------
    proc : tupla
        (tuit, ranking)         
    hechos : lista
        de indices (int) de la lista de tuits que ya están rankeados
    revisar : lista
        de indices (int) de la lista de tuits que quedaron para revisar
    """
    pendientes = [x for x in range(len(tuits)) if x not in hechos + revisar]
    puntuaciones = {"P":1, "N":-1, "O":0}
    for act in pendientes:
        t = tuits[act]
        texto = instruc+t+botones
        l = input(texto)
        while l not in ['N', 'P', 'O', 'S', 'R']:
            print('\033[31m'+'ERROR: Comando no válido'+'\033[0m')
            l = input(texto)
        if l in ['P','N','O']:
            hechos.append(act)
            proc.append((t, puntuaciones[l]))
        elif l == 'R':
            revisar.append(act)
            pass
        else:     

            break
    pendientes = [x for x in range(len(tuits)) if x not in hechos + revisar]
    print('Total de {:d} tuit(s) clasificado(s), {:d} pendiente(s), {:d} marcado(s) para revisión.'.format(len(hechos), len(pendientes), len(revisar)))        
    # return proc, hechos, revisar  
    return None

def rev(tuits, proc = proc, hechos = hechos, revisar = revisar):
    """
    Toma sólo los tuits marcados para revisón y los etiqueta.
    Parámetros
    ----------
    tuits : lista de tuits, strings
    proc : tupla
        (tuit, ranking)         
    hechos : lista
        de indices (int) de la lista de tuits que ya están rankeados
    revisar : lista
        de indices (int) de la lista de tuits que quedaron para revisar

    Salida
    -------
    proc : tupla
        (tuit, ranking)         
    hechos : lista
        de indices (int) de la lista de tuits que ya están rankeados
    revisar : lista
        de indices (int) de la lista de tuits que quedaron para revisar
    """
    puntuaciones = {"P":1, "N":-1, "O":0}
    revisados = 0
    for act in revisar:
        t = tuits[act]
        texto = instruc2 + t + botones
        l = input(texto)
        while l not in ['N', 'P', 'O', 'S', 'R']:
            print('\033[31m'+'ERROR: Comando no válido'+'\033[0m')
            l = input(texto)
        if l in ['P','N','O']:
            hechos.append(act)
            proc.append((t, puntuaciones[l]))
            revisados += 1
        elif l == 'R':
            pass
        else:     
            break
    revisar = [x for x in revisar if x not in hechos]
    print('Total de {:d} tuit(s) revisado(s), {:d} pendiente(s) de revisión.'.format(revisados, len(revisar)))
    return None


rankear(tuits)
rev(tuits)
