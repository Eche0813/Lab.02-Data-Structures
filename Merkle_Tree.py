"""
Módulo de Árboles de Merkle con Balanceo Par en Todos los Niveles.

Proporciona la representación e implementación de una estructura de datos de 
Árbol de Merkle (Merkle Tree) orientada a la simulación de bloques de criptomonedas
o registros de Git.

Asegura un balanceo par estricto duplicando el último elemento/nodo en caso de
encontrar una cantidad impar tanto en el nivel 0 (hojas) como en cualquier nivel
interno intermedio durante la construcción recursiva.

Compatibilidad: Python 3.9+
"""

import hashlib
from typing import List, Tuple, Optional


class MerkleNode:
    """
    Representa un nodo individual (hoja o nodo interno) en el Árbol de Merkle.

    Attributes:
        left (Optional[MerkleNode]): Puntero hacia el hijo izquierdo.
        right (Optional[MerkleNode]): Puntero hacia el hijo derecho.
        data (Optional[str]): Transacción o contenido en texto plano (solo en hojas).
        hash (str): Hash SHA-256 en formato hexadecimal asignado o derivado.
    """

    def __init__(
        self,
        left: Optional['MerkleNode'] = None,
        right: Optional['MerkleNode'] = None,
        data: Optional[str] = None,
        hash_val: Optional[str] = None
    ) -> None:
        """
        Inicializa un nodo del árbol.

        Si se proporciona `hash_val`, se asigna directamente (útil para duplicaciones).
        Si se pasa `data`, se calcula el hash SHA-256 del contenido (nodo hoja).
        De lo contrario, se deriva concatenando los hashes de `left` y `right` (nodo interno).

        Args:
            left: Instancia del nodo hijo izquierdo (opcional).
            right: Instancia del nodo hijo derecho (opcional).
            data: Contenido de texto plano para un nodo hoja (opcional).
            hash_val: Hash prefijado explícitamente (opcional).

        Raises:
            AssertionError: Si no se proveen ambos hijos para la creación de un nodo interno.
        """
        self.left: Optional['MerkleNode'] = left
        self.right: Optional['MerkleNode'] = right
        self.data: Optional[str] = data

        if hash_val:
            self.hash: str = hash_val
        elif data is not None:
            self.hash = self._hash_data(data)
        else:
            assert left is not None and right is not None, "Un nodo interno requiere ambos hijos."
            self.hash = self._hash_data(left.hash + right.hash)

    @staticmethod
    def _hash_data(data: str) -> str:
        """
        Genera el hash SHA-256 en formato hexadecimal para una cadena codificada en UTF-8.

        Args:
            data (str): Cadena de texto a procesar.

        Returns:
            str: Hash de 64 caracteres en representación hexadecimal.
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()


class MerkleTree:
    """
    Gestiona la construcción, verificación y recorrido de un Árbol de Merkle.

    Attributes:
        elements (List[str]): Lista de transacciones u objetos en texto plano.
        logs_balanceo (List[str]): Registro cronológico de duplicaciones realizadas por paridad.
        leaves (List[MerkleNode]): Lista de nodos hoja del nivel base.
        root (MerkleNode): Nodo raíz principal que contiene la Merkle Root.
    """

    def __init__(self, elements: List[str]) -> None:
        """
        Inicializa y construye el Árbol de Merkle garantizando paridad en las hojas.

        Args:
            elements (List[str]): Lista original de transacciones o entradas de datos.

        Raises:
            ValueError: Si la lista de entrada está vacía.
        """
        if not elements:
            raise ValueError("No se puede crear un árbol sin elementos.")

        self.elements: List[str] = list(elements)
        self.logs_balanceo: List[str] = []

        # Nivel 0 (Hojas): Si la cantidad de datos es impar, se duplica el último elemento
        if len(self.elements) % 2 != 0 and len(self.elements) > 1:
            self.elements.append(self.elements[-1])
            self.logs_balanceo.append(
                f"Nivel 0 (Hojas): Se duplicó la hoja final '{self.elements[-1]}'."
            )

        self.leaves: List[MerkleNode] = [MerkleNode(data=e) for e in self.elements]
        self.root: MerkleNode = self._build_tree(self.leaves, level=1)

    def _build_tree(self, nodes: List[MerkleNode], level: int) -> MerkleNode:
        """
        Construye recursivamente los niveles del árbol combinando pares de nodos.

        Si en un nivel determinado la cantidad de nodos es impar, duplica el último
        nodo asociándolo consigo mismo para mantener la paridad.

        Args:
            nodes (List[MerkleNode]): Nodos pertenecientes al nivel actual.
            level (int): Identificador numérico del nivel actual (usado para logs).

        Returns:
            MerkleNode: El nodo raíz una vez alcanzado el tope del árbol.
        """
        if len(nodes) == 1:
            return nodes[0]

        # REGLA DE BALANCEO: Si el nivel actual es impar, duplicar el último nodo
        if len(nodes) % 2 != 0:
            nodo_duplicado = MerkleNode(data=nodes[-1].data, hash_val=nodes[-1].hash)
            nodes.append(nodo_duplicado)

            tipo = f"Hoja '{nodes[-1].data}'" if nodes[-1].data else f"Nodo Hash [{nodes[-1].hash[:8]}...]"
            self.logs_balanceo.append(
                f"Nivel {level} (Interno): Cantidad impar ({len(nodes)-1} nodos). Se duplicó el {tipo}."
            )

        next_level: List[MerkleNode] = []
        for i in range(0, len(nodes), 2):
            parent = MerkleNode(left=nodes[i], right=nodes[i + 1])
            next_level.append(parent)

        return self._build_tree(next_level, level + 1)

    def print_tree(self, node: Optional[MerkleNode] = None, level: int = 0) -> None:
        """
        Imprime de forma recursiva la jerarquía visual del árbol en consola.

        Args:
            node (Optional[MerkleNode]): Nodo sobre el cual iniciar la impresión.
            level (int): Profundidad actual empleada para calcular la sangría visual.
        """
        if node is None:
            node = self.root

        indent = "  " * level
        node_type = f"[HOJA: '{node.data}']" if node.data is not None else "[NODO INTERNO]"
        print(f"{indent}└── {node_type} Hash: {node.hash[:12]}...")

        if node.left:
            self.print_tree(node.left, level + 1)
        if node.right:
            self.print_tree(node.right, level + 1)

    def get_proof(self, target_data: str) -> Optional[List[Tuple[str, str]]]:
        """
        Genera una Merkle Proof (prueba de inclusión) para una transacción dada.

        Args:
            target_data (str): Cadena exacta de la transacción que se desea verificar.

        Returns:
            Optional[List[Tuple[str, str]]]: Lista de pares `(hash_hermano, posicion)`
            que componen la prueba, o `None` si la transacción no existe en las hojas.
        """
        target_hash = MerkleNode._hash_data(target_data)
        current_level = list(self.leaves)

        index = -1
        for idx, node in enumerate(current_level):
            if node.hash == target_hash:
                index = idx
                break

        if index == -1:
            return None

        proof: List[Tuple[str, str]] = []

        while len(current_level) > 1:
            if len(current_level) % 2 != 0:
                current_level.append(MerkleNode(data=current_level[-1].data, hash_val=current_level[-1].hash))

            is_right = (index % 2 == 1)
            sibling_index = index - 1 if is_right else index + 1
            sibling_hash = current_level[sibling_index].hash
            direction = 'left' if is_right else 'right'

            proof.append((sibling_hash, direction))

            next_level: List[MerkleNode] = []
            for i in range(0, len(current_level), 2):
                next_level.append(MerkleNode(left=current_level[i], right=current_level[i + 1]))

            current_level = next_level
            index //= 2

        return proof

    @staticmethod
    def verify_proof(target_data: str, proof: List[Tuple[str, str]], root_hash: str) -> bool:
        """
        Valida criptográficamente si una prueba pertenece a un hash raíz específico.

        Args:
            target_data (str): Transacción a validar.
            proof (List[Tuple[str, str]]): Camino de prueba retornado por `get_proof`.
            root_hash (str): Hash de la raíz con la cual comparar el resultado.

        Returns:
            bool: `True` si el cálculo derivado coincide con `root_hash`, `False` en caso contrario.
        """
        current_hash = MerkleNode._hash_data(target_data)

        for sibling_hash, direction in proof:
            if direction == 'left':
                combined = sibling_hash + current_hash
            else:
                combined = current_hash + sibling_hash
            current_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()

        return current_hash == root_hash


# ==========================================
# INTERFAZ DE CONSOLA Y MENÚ
# ==========================================

def ingresar_transacciones() -> Optional[MerkleTree]:
    """
    Gestiona la captura interactiva de transacciones mediante la consola estándar.

    Returns:
        Optional[MerkleTree]: Instancia de `MerkleTree` creada, o `None` si la entrada es inválida.
    """
    print("\n--- INGRESO DE DATOS ---")
    transacciones: List[str] = []
    try:
        n = int(input("¿Cuántas transacciones/datos deseas ingresar?: "))
    except ValueError:
        print("Entrada inválida. Se debe ingresar un número entero.")
        return None

    for i in range(1, n + 1):
        tx = input(f"Ingrese transacción #{i}: ").strip()
        if tx:
            transacciones.append(tx)

    if not transacciones:
        print("No se ingresó ninguna transacción válida.")
        return None

    tree = MerkleTree(transacciones)
    print("\n ¡Árbol construido con éxito!")
    print(f"MERKLE ROOT (Raíz): {tree.root.hash}")
    return tree


def main() -> None:
    """Bucle principal de la aplicación que administra las opciones del menú."""
    print("==========================================")
    print("      CONSTRUCTOR DE ÁRBOLES DE MERKLE    ")
    print("==========================================")

    tree: Optional[MerkleTree] = ingresar_transacciones()
    while tree is None:
        tree = ingresar_transacciones()

    while True:
        print("\n" + "=" * 42)
        print("            MENÚ DE OPCIONES              ")
        print("=" * 42)
        print("1. Verificar una transacción (Merkle Proof)")
        print("2. Ver estructura visual del árbol")
        print("3. Ver historial de balanceo por niveles")
        print("4. Ver Merkle Root actual")
        print("5. Crear un nuevo árbol (Reiniciar datos)")
        print("6. Salir")

        opcion = input("\nSelecciona una opción (1-6): ").strip()

        if opcion == "1":
            print("\n--- VERIFICACIÓN DE INCLUSIÓN ---")
            tx_to_verify = input("Ingresa la transacción exacta a verificar: ").strip()

            proof = tree.get_proof(tx_to_verify)

            if proof is None:
                print(f"\nRECHAZADO: La transacción '{tx_to_verify}' NO pertenece al árbol.")
            else:
                print(f"\n Transacción encontrada en la lista de hojas.")
                print(f"Longitud de la prueba (Camino de hashes): {len(proof)}")

                is_valid = MerkleTree.verify_proof(tx_to_verify, proof, tree.root.hash)
                if is_valid:
                    print("Resultado matemático: VÁLIDO (True)")

        elif opcion == "2":
            print("\n--- ESTRUCTURA DEL ÁRBOL ---")
            tree.print_tree()

        elif opcion == "3":
            print("\n--- HISTORIAL DE DUPLICACIONES POR NIVEL ---")
            if not tree.logs_balanceo:
                print("El árbol era completamente par en todos sus niveles. No se requirieron duplicaciones.")
            else:
                for log in tree.logs_balanceo:
                    print(f"• {log}")

        elif opcion == "4":
            print(f"\n MERKLE ROOT: {tree.root.hash}")

        elif opcion == "5":
            nuevo_arbol = ingresar_transacciones()
            if nuevo_arbol:
                tree = nuevo_arbol

        elif opcion == "6":
            print("\n¡Hasta luego!")
            break

        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()