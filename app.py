from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Archivo para almacenar las transacciones
DATA_FILE = 'transacciones.json'

# Cargar transacciones existentes o inicializar lista vacía
def cargar_transacciones():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# Guardar transacciones en el archivo
def guardar_transacciones(transacciones):
    with open(DATA_FILE, 'w') as f:
        json.dump(transacciones, f, indent=2)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Obtener todas las transacciones
@app.route('/transacciones', methods=['GET'])
def obtener_transacciones():
    transacciones = cargar_transacciones()
    return jsonify(transacciones)

# Agregar una nueva transacción
@app.route('/transacciones', methods=['POST'])
def agregar_transaccion():
    transacciones = cargar_transacciones()
    
    nueva_transaccion = request.get_json()
    
    # Validar datos
    if not all(key in nueva_transaccion for key in ['tipo', 'concepto', 'monto', 'fecha', 'categoria']):
        return jsonify({'error': 'Datos incompletos'}), 400
    
    try:
        nueva_transaccion['monto'] = float(nueva_transaccion['monto'])
        if nueva_transaccion['monto'] <= 0:
            return jsonify({'error': 'El monto debe ser positivo'}), 400
    except ValueError:
        return jsonify({'error': 'Monto inválido'}), 400
    
    # Asignar ID (simplificado para este ejemplo)
    nueva_transaccion['id'] = len(transacciones) + 1
    
    # Validar fecha
    try:
        datetime.strptime(nueva_transaccion['fecha'], '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
    
    transacciones.append(nueva_transaccion)
    guardar_transacciones(transacciones)
    
    return jsonify(nueva_transaccion), 201

# Eliminar una transacción
@app.route('/transacciones/<int:id>', methods=['DELETE'])
def eliminar_transaccion(id):
    transacciones = cargar_transacciones()
    transaccion_eliminada = None
    
    for i, transaccion in enumerate(transacciones):
        if transaccion['id'] == id:
            transaccion_eliminada = transacciones.pop(i)
            break
    
    if transaccion_eliminada:
        guardar_transacciones(transacciones)
        return jsonify(transaccion_eliminada), 200
    else:
        return jsonify({'error': 'Transacción no encontrada'}), 404

if __name__ == '__main__':
    app.run(debug=True)