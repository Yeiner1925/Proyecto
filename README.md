python
class Juego:
    """Clase base para todas las entidades del juego"""
    
    def __init__(self, nombre: str, posicion: tuple):
        self.nombre = nombre
        self.posicion = posicion  # Tupla (x, y) para coordenadas
    
    def mover(self, nueva_x: int, nueva_y: int):
        """Cambia la posición del elemento en el escenario"""
        if nueva_x < 0 or nueva_y < 0:  # Validar que las coordenadas sean positivas
            raise ValueError("Las coordenadas deben ser valores positivos.")
        self.posicion = (nueva_x, nueva_y)
    
    def __str__(self):
        """Representación string de la entidad"""
        return f"{self.nombre} - Posición: {self.posicion}"


class Jugador(Juego):
    """Clase que representa al jugador principal"""
    
    VIDA_INICIAL = 3  # Definimos constante para la vida inicial
    
    def __init__(self, nombre: str, posicion: tuple):
        super().__init__(nombre, posicion)
        self.vida = self.VIDA_INICIAL
        self.poderes = []  # Lista para almacenar los poderes
        self.puntaje = 0  # Inicializamos el puntaje
    
    def obtener_poder(self, poder):
        """Añade un nuevo poder a la colección del jugador"""
        self.poderes.append(poder)
    
    def mostrar_poderes(self):
        """Muestra los poderes del jugador"""
        if not self.poderes:
            return "No tiene poderes"
        return "\n".join(f"- {poder.nombre}: {poder.descripcion}" for poder in self.poderes)
    
    def aumentar_puntaje(self, puntos: int):
        """Aumenta el puntaje del jugador"""
        if puntos < 0:
            raise ValueError("Los puntos no pueden ser negativos.")
        self.puntaje += puntos
    
    def __str__(self):
        """Representación extendida del jugador"""
        info_base = super().__str__()
        poderes_info = self.mostrar_poderes()
        return (f"{info_base}\n"
                f"Vidas: {self.vida}\n"
                f"Puntaje: {self.puntaje}\n"
                f"Poderes:\n{poderes_info}")


class Enemigo(Juego):
    """Clase que representa a los enemigos del juego"""
    
    def __init__(self, nombre: str, posicion: tuple, tipo: str):
        super().__init__(nombre, posicion)
        self.tipo = tipo  # Tipo específico de enemigo
    
    def atacar(self, jugador: Jugador):
        """Método para simular un ataque al jugador"""
        print(f"{self.nombre} ataca a {jugador.nombre}!")
        jugador.vida -= 1
        if jugador.vida <= 0:
            print(f"{jugador.nombre} ha sido derrotado.")
    
    def __str__(self):
        """Representación extendida del enemigo"""
        return f"{super().__str__()} (Tipo: {self.tipo})"


class Poder:
    """Clase para los power-ups del juego"""
    
    def __init__(self, nombre: str, descripcion: str):
        self.nombre = nombre
        self.descripcion = descripcion
    
    def aplicar(self, jugador: Jugador):
        """Método para aplicar el poder al jugador"""
        print(f"{jugador.nombre} ha obtenido el poder: {self.nombre}")
        
    def __str__(self):
        """Representación string del poder"""
        return f"{self.nombre}: {self.descripcion}"


def main():
    print("=== SUPER MARIO BROS ===")
    
    # Crear jugador
    mario = Jugador("Mario", (0, 0))
    print("\nJugador creado en posición inicial:", mario.posicion)
    
    # Crear enemigos
    enemigos = [
        Enemigo("Goomba 1", (5, 0), "Goomba"),
        Enemigo("Koopa 1", (7, 2), "Koopa Troopa")
    ]
    print(f"\nSe han creado {len(enemigos)} enemigos.")
    
    # Crear poderes
    hongo = Poder("Super Hongo", "Hace que Mario crezca")
    flor = Poder("Flor de Fuego", "Permite lanzar bolas de fuego")
    
    # Asignar poderes al jugador
    mario.obtener_poder(hongo)
    mario.obtener_poder(flor)
    
    # Aplicar poderes al jugador
    hongo.aplicar(mario)
    
    print("\nPoderes asignados al jugador.")
    
    # Mover al jugador y aumentar puntaje
    try:
        mario.mover(3, 1)
        mario.aumentar_puntaje(100)  # Aumentamos el puntaje por moverse
        print(f"\nEl jugador se ha movido a {mario.posicion}. Puntaje actual: {mario.puntaje}.")
        
    except ValueError as e:
        print(f"\nError al mover al jugador: {e}")
    
    # Simular ataque de enemigo
    for enemigo in enemigos:
        enemigo.atacar(mario)  # Cada enemigo ataca al jugador una vez
    
    # Mostrar información del juego
    print("\n=== ESTADO ACTUAL DEL JUEGO ===")
    
    print("\nJUGADOR:")
    print(mario)
    
    print("\nENEMIGOS:")
    for enemigo in enemigos:
        print(enemigo)


if __name__ == "__main__":
    main()

