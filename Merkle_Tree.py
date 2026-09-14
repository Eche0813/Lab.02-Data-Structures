"""
Módulo de Árboles de Merkle con Balanceo Par en Todos los Niveles.

Garantiza que tanto el nivel de hojas como cualquier nivel intermedio impar
duplique su último nodo para concatenarlo consigo mismo.

Compatibilidad: Python 3.9+
"""

import hashlib
from typing import List, Tuple, Optional


class MerkleNode:
    """Representa un nodo dentro de la estructura del Árbol de Merkle."""

    def __init__(
        self,
        left: Optional['MerkleNode'] = None,
        right: Optional['MerkleNode'] = None,
        data: Optional[str] = None,
        hash_val: Optional[str] = None
    ) -> None:
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
        return hashlib.sha256(data.encode('utf-8')).hexdigest()


class MerkleTree:
    """
    Gestiona el Árbol de Merkle asegurando paridad estricta en todos los niveles.
    """

    def __init__(self, elements: List[str]) -> None:
        if not elements:
            raise ValueError("No se puede crear un árbol sin elementos.")

        self.elements: List[str] = list(elements)
        self.logs_balanceo: List[str] = []

        # Nivel 0 (Hojas): Si es impar, se duplica el último elemento
        if len(self.elements) % 2 != 0 and len(self.elements) > 1:
            self.elements.append(self.elements[-1])
            self.logs_balanceo.append(
                f"Nivel 0 (Hojas): Se duplicó la hoja final '{self.elements[-1]}'."
            )

        self.leaves: List[MerkleNode] = [MerkleNode(data=e) for e in self.elements]
        self.root: MerkleNode = self._build_tree(self.leaves, level=1)

    def _build_tree(self, nodes: List[MerkleNode], level: int) -> MerkleNode:
        """
        Construye el árbol recursivamente. 
        Si encuentra una cantidad impar de nodos en cualquier nivel, 
        duplica el último nodo asociándolo consigo mismo.
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
        """Imprime la estructura jerárquica del árbol."""
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
        """Genera la prueba de inclusión (Merkle Proof) para una transacción."""
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
        """Verifica de forma independiente una Merkle Proof."""
        current_hash = MerkleNode._hash_data(target_data)

        for sibling_hash, direction in proof:
            if direction == 'left':
                combined = sibling_hash + current_hash
            else:
                combined = current_hash + sibling_hash
            current_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()

        return current_hash == root_hash


# ==========================================
# INTERFAZ DE CONSOLA
# ==========================================

def ingresar_transacciones() -> Optional[MerkleTree]:
    print("\n--- INGRESO DE DATOS ---")
    transacciones: List[str] = []
    try:
        n = int(input("¿Cuántas transacciones/datos deseas ingresar?: "))
    except ValueError:
        print("❌ Entrada inválida. Se debe ingresar un número entero.")
        return None

    for i in range(1, n + 1):
        tx = input(f"Ingrese transacción #{i}: ").strip()
        if tx:
            transacciones.append(tx)

    if not transacciones:
        print("❌ No se ingresó ninguna transacción válida.")
        return None

    tree = MerkleTree(transacciones)
    print("\n✅ ¡Árbol construido con éxito!")
    print(f"MERKLE ROOT (Raíz): {tree.root.hash}")
    return tree


def main() -> None:
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
                print(f"\n❌ RECHAZADO: La transacción '{tx_to_verify}' NO pertenece al árbol.")
            else:
                print(f"\n✅ Transacción encontrada en la lista de hojas.")
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
                print("✨ El árbol era completamente par en todos sus niveles. No se requirieron duplicaciones.")
            else:
                for log in tree.logs_balanceo:
                    print(f"• {log}")

        elif opcion == "4":
            print(f"\n📌 MERKLE ROOT: {tree.root.hash}")

        elif opcion == "5":
            nuevo_arbol = ingresar_transacciones()
            if nuevo_arbol:
                tree = nuevo_arbol

        elif opcion == "6":
            print("\n¡Hasta luego!")
            break

        else:
            print("❌ Opción inválida.")


if __name__ == "__main__":
    main()