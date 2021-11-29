import numpy as np
from PIL import Image

def addToClass(cl):
    ''' D�corateur permettant d'ajouter la fonction d�cor�e en tant que m�thode
    � une classe.
    
    Permet d'impl�menter une forme �l�mentaire de programmation orient�e
    aspects en regroupant les m�thodes de diff�rentes classes impl�mentant
    une m�me fonctionnalit� en un seul endroit.
    
    Attention, apr�s utilisation de ce d�corateur, la fonction d�cor�e reste dans
    le namespace courant. Si cela d�range, on peut utiliser del pour la d�truire.
    Je ne sais pas s'il existe un moyen d'�viter ce ph�nom�ne.
    '''
    def decorator(func):
        setattr(cl,func.__name__,func)
        return func
    return decorator


def a():
    from ast import literal_eval
    x = literal_eval('(3, 4, 5)')
    print(x)

def main():
    a()
    return
    size = 1024
    data = np.empty((size, size, 3), dtype=np.uint8)
    print(data)
    data.fill([255, 0, 0])

    # for i in range(size):
    #     for j in range(size):
    #         data[i, j] = (128, 0, 80)
            
    i = Image.fromarray(data, 'RGB')
    i.show()
    i.save('output.png')

if __name__ == '__main__':
    main()