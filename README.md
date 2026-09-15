# Laboratorio 02 - Estructuras de Datos: Árbol Merkle - Samuel Echeverri Ortiz

Este proyecto se basa en la implementación interactiva en Python de la estructura de datos Árbol de Merkle (Merkle Tree), diseñada para simular la verificación criptográfica de datos utilizada en sistemas de transacciones.

---

## Características principales

- **Criptografía SHA-256:** Generación de hashes estándar para garantizar la integridad de las transacciones o registros.
- **Balanceo Par Estricto por Nivel:** Manejo automático de conjuntos de datos impares. Si un nivel (sea el nivel 0 de hojas o cualquier nivel interno intermedio) contiene una cantidad impar de nodos, el último nodo se duplica automáticamente para formar la pareja.
- **Generación de Merkle Proofs (Pruebas de Inclusión):** Construcción del camino mínimo de hashes hermanos ($O(\log n)$) necesario para validar la pertenencia de un elemento.
- **Verificación Independiente:** Método estático para validar la autenticidad de una transacción usando únicamente la Merkle Root y la prueba provista.
- **Interfaz de Consola Interactiva (CLI):** Menú persistente que permite crear árboles en tiempo real, visualizar la jerarquía del árbol, consultar la raíz y revisar auditorías de balanceo.

---

## Estructura del código

El código está completamente estructurado de acuerdo con el estándar PEP 257 (Docstrings) e incluye anotaciones de tipos explícitas (Type Hints):

    MerkleNode: Clase que representa cada nodo (hoja o nodo interno) del árbol.

    MerkleTree: Clase principal que gestiona la construcción recursiva del árbol, las duplicaciones por paridad, la generación de pruebas de inclusión (get_proof) y la verificación matemática (verify_proof).

    ingresar_transacciones() & main(): Funciones auxiliares que controlan el menú de navegación y la interacción por consola.

---
## Requisitos
- Phyton 3.9 o superior
- No requiere dependencias externas (utiliza únicamente módulos de la librería estándar de Python como hashlib y typing).
---
## Uso e interfaz
Al iniciar el programa, se te solicitará ingresar la cantidad y el contenido de las transacciones base:
==========================================
      CONSTRUCTOR DE ÁRBOLES DE MERKLE    
==========================================

--- INGRESO DE DATOS ---

¿Cuántas transacciones/datos deseas ingresar?: 3

Ingrese transacción #1: Alice -> Bob: 1.5 BTC

Ingrese transacción #2: Bob -> Charlie: 0.5 BTC

Ingrese transacción #3: Charlie -> Dave: 0.2 BTC

¡Árbol construido con éxito!

MERKLE ROOT (Raíz):
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

Opciones del Menú

    1. Verificar una transacción (Merkle Proof): Ingresa una cadena de texto para verificar si está presente en la Merkle Root actual.

    2. Ver estructura visual del árbol: Muestra la jerarquía de nodos junto con los primeros caracteres de sus hashes SHA-256.

    3. Ver historial de balanceo por niveles: Muestra qué nodos u hojas fueron duplicados para corregir paridades impares durante la construcción.

    4. Ver Merkle Root actual: Imprime el hash raíz completo de 64 caracteres en hexadecimal.

    5. Crear un nuevo árbol: Reinicia la estructura permitiendo ingresar un nuevo lote de datos.

    6. Salir: Finaliza la ejecución del script.

## Uso de IA generativa
Afirmo haber usado IA generativa y me hago completamente responsable de su uso **única y exclusivamente para**:
- Implementación y comprensión de librería typing en el código.
- Creación de "interfaz visual" en la terminal y menú de opciones.
- Documentación completa y estructurada del código según el estándar PEP 257 e inclusión de type hints.
- Acompañamiento en la creación ordenada de este documento README.md.