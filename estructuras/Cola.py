class Nodo: 
    def __init__(self,info):
        self.info = info #informacion del nodo, puntero
        self.siguiente = None 

    def obtenerInfo(self):
        return self.info
    def obtenerSiguiente(self):
        return self.siguiente

    def asignarInfo(self,info):
        self.info = info
    def asignarSiguiente(self,nuevosiguiente):
        self.siguiente = nuevosiguiente


class Cola: 

    def __init__(self):
        self.primero = None#tiene 2 punteros, uno al primero y otro al siguiente
        self.ultimo = None

    def estaVacia(self):
        return self.primero == None

    def Push(self,item):
        nuevo = Nodo(item) 
        
        if self.primero != None: #apunta al ultimo y lo agrega al final
            self.ultimo.asignarSiguiente(nuevo)
        else:
            self.primero = nuevo
            
        self.ultimo = nuevo
            
    def tamano(self):
        actual = self.primero
        contador = 0
        while actual != None:
            contador = contador + 1
            actual = actual.obtenerSiguiente()
        return contador

    def desplegar(self):
        actual = self.primero
        while actual != None:
            actual.obtenerInfo().desplegar()
            actual = actual.obtenerSiguiente()

    def buscar(self,item):
        actual = self.primero
        encontrado = False
        while actual != None and not encontrado:
            if actual.obtenerInfo().EsIgualALLave(item):
                encontrado = True
            else:
                actual = actual.obtenerSiguiente()

        return encontrado

    def Pop(self): #hace el enlace al inicio de la cola
        primerotemp = self.primero 
        if self.primero != None:
            # No llamar a desplegar() aquí: Pop debe devolver el info del nodo
            self.primero = self.primero.obtenerSiguiente()
        else:
            print("Cola esta vacia")
            return None
            
        return primerotemp.obtenerInfo() #devuelve la informacion del nodo que estaba en el frente de la cola
    