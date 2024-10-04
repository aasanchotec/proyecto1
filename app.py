from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from conectarBD import conectar_bd

app = Flask(__name__)
app.secret_key = 'tu_super_secreto'
app.config['SESSION_TYPE'] = 'filesystem'

def handle_collection_actions(nombre):
    db = conectar_bd()
    collection = db[nombre]
    document_fields = collection.find_one()  # Asegúrate de gestionar None si no hay documentos
    if request.method == 'POST':
        action = request.form.get('action')
        # Implementa la lógica de las acciones aquí, como agregar, actualizar, etc.
        # Utiliza 'flash()' para mensajes y 'redirect()' para redirigir según sea necesario
    # Pasa variables necesarias a la plantilla
    return render_template('manage_collection.html', fields=document_fields, nombre_coleccion=nombre)


#festividades

@app.route('/herencias/festividades', methods=['GET', 'POST'])
def manage_festividades():
    client = conectar_bd()
    if not client:
        flash('No se pudo conectar a la base de datos.', 'error')
        return redirect(url_for('manage_festividades'))
    
    db = client['herencias']
    collection = db['Festividades']
    
    document_fields = collection.find_one()  # Encuentra el primer documento en la colección.

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'Agregar':
            documento = {
                'Nombre_Original': request.form.get('Nombre_Original', '').strip(),
                'fecha': request.form.get('fecha', '').strip(),
                'actividades': request.form.get('actividades', '').strip(),
                'quien_puede_asistir': request.form.get('quien_puede_asistir', '').strip(),
                'implicaciones': request.form.get('implicaciones', '').strip(),
            }
            if all(value != '' for value in documento.values()):
                resultado = collection.insert_one(documento)
                registrar_operacion(session['nombre_usuario'], 'Agregar', 'Festividades', str(resultado.inserted_id))
                flash(f"Documento agregado con éxito, ID: {resultado.inserted_id}", 'success')
            else:
                flash("Debe llenar todos los campos requeridos.", 'error')

        elif action == 'Actualizar':
            documento_id = request.form.get('_id')
            cambios = {k: v for k, v in request.form.items() if k != 'action' and k != '_id' and request.form.get('update_' + k)}
            if documento_id and cambios:
                resultado = collection.update_one({'_id': ObjectId(documento_id)}, {'$set': cambios})
                if resultado.modified_count:
                    registrar_operacion(session['nombre_usuario'], 'Actualizar', 'Festividades', documento_id)
                flash("Documento actualizado correctamente." if resultado.modified_count else "No se actualizó ningún documento.", 'success' if resultado.modified_count else 'error')
            else:
                flash("Debe proporcionar un ID válido y seleccionar los campos a actualizar.", 'error')

        elif action == 'Eliminar':
            documento_id = request.form.get('_id')
            if documento_id:
                resultado = collection.delete_one({'_id': ObjectId(documento_id)})
                if resultado.deleted_count > 0:
                    registrar_operacion(session['nombre_usuario'], 'Eliminar', 'Festividades', documento_id)
                flash("Documento eliminado correctamente." if resultado.deleted_count else "No se encontró el documento a eliminar.", 'success' if resultado.deleted_count else 'error')
            else:
                flash("Debe proporcionar un ID válido para eliminar.", 'error')

        elif action == 'Consultar':
            documento_id = request.form.get('_id')
            documento = collection.find_one({'_id': ObjectId(documento_id)})
            if documento:
                return render_template('manage_festividades.html', documentos=[documento], modo='ver_todo')
            else:
                flash("No se encontró el documento.", 'error')

        elif action == 'Ver Todo':
            documentos = list(collection.find())
            return render_template('manage_festividades.html', documentos=documentos, modo='ver_todo')

        elif action == 'Salir':
            return redirect(url_for('index'))
            
    return render_template('manage_festividades.html', fields=document_fields if document_fields else {}, nombre_coleccion='Festividades')

###Ingredientes
@app.route('/herencias/ingredientes', methods=['GET', 'POST'])
def manage_ingredientes():
    client = conectar_bd()
    if not client:
        flash('No se pudo conectar a la base de datos.', 'error')
        return redirect(url_for('manage_ingredientes'))
    
    db = client['herencias']
    collection = db['Ingredientes']
    
    document_fields = collection.find_one()  # Encuentra el primer documento en la colección.

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'Agregar':
            documento = {k: v for k, v in request.form.items() if k != 'action' and v.strip()}
            if document_fields and all(documento.get(key) for key in document_fields.keys() if key != '_id'):
                resultado = collection.insert_one(documento)
                if resultado.acknowledged:
                    registrar_operacion(session['nombre_usuario'], 'Agregar', 'Ingredientes', str(resultado.inserted_id))
                flash(f"Documento agregado con éxito, ID: {resultado.inserted_id}", 'success')
            else:
                flash("Debe llenar todos los campos requeridos.", 'error')

        elif action == 'Actualizar':
            documento_id = request.form.get('_id')
            cambios = {k: v for k, v in request.form.items() if k != 'action' and k != '_id' and request.form.get('update_' + k)}
            if documento_id and cambios:
                resultado = collection.update_one({'_id': ObjectId(documento_id)}, {'$set': cambios})
                if resultado.modified_count:
                    registrar_operacion(session['nombre_usuario'], 'Actualizar', 'Ingredientes', documento_id)
                flash("Documento actualizado correctamente." if resultado.modified_count else "No se actualizó ningún documento.", 'success' if resultado.modified_count else 'error')
            else:
                flash("Debe proporcionar un ID válido y seleccionar los campos a actualizar.", 'error')

        elif action == 'Eliminar':
            documento_id = request.form.get('_id')
            if documento_id:
                resultado = collection.delete_one({'_id': ObjectId(documento_id)})
                if resultado.deleted_count:
                    registrar_operacion(session['nombre_usuario'], 'Eliminar', 'Ingredientes', documento_id)
                flash("Documento eliminado correctamente." if resultado.deleted_count else "No se encontró el documento a eliminar.", 'success' if resultado.deleted_count else 'error')
            else:
                flash("Debe proporcionar un ID válido para eliminar.", 'error')

        elif action == 'Consultar':
            documento_id = request.form.get('_id')
            documento = collection.find_one({'_id': ObjectId(documento_id)})
            if documento:
                # Muestra solo el documento consultado
                return render_template('manage_ingredientes.html', documentos=[documento], modo='ver_todo')
            else:
                flash("No se encontró el documento.", 'error')

        elif action == 'Ver Todo':
            documentos = list(collection.find())
            return render_template('manage_ingredientes.html', documentos=documentos, modo='ver_todo')

        elif action == 'Salir':
            return redirect(url_for('index'))
            
    return render_template('manage_ingredientes.html', fields=document_fields if document_fields else {}, nombre_coleccion='Ingredientes')

##poblaciones 

@app.route('/herencias/poblaciones', methods=['GET', 'POST'])
def manage_poblaciones():
    client = conectar_bd()
    if not client:
        flash('No se pudo conectar a la base de datos.', 'error')
        return redirect(url_for('manage_poblaciones'))
    
    db = client['herencias']
    collection = db['Poblaciones']
    
    document_fields = collection.find_one()  # Encuentra el primer documento en la colección.

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'Agregar':
            documento = {k: v for k, v in request.form.items() if k != 'action' and k != '_id' and v.strip()}
            resultado = collection.insert_one(documento)
            if resultado.acknowledged:
                registrar_operacion(session['nombre_usuario'], 'Agregar', 'Poblaciones', str(resultado.inserted_id))
            flash(f"Documento agregado con éxito, ID: {resultado.inserted_id}", 'success')

        elif action == 'Actualizar':
            documento_id = request.form.get('_id')
            cambios = {k: v for k, v in request.form.items() if k != 'action' and k != '_id' and request.form.get('update_' + k)}
            if documento_id and cambios:
                resultado = collection.update_one({'_id': ObjectId(documento_id)}, {'$set': cambios})
                if resultado.modified_count:
                    registrar_operacion(session['nombre_usuario'], 'Actualizar', 'Poblaciones', documento_id)
                flash("Documento actualizado correctamente." if resultado.modified_count else "No se actualizó ningún documento.", 'success' if resultado.modified_count else 'error')

        elif action == 'Eliminar':
            documento_id = request.form.get('_id')
            if documento_id:
                resultado = collection.delete_one({'_id': ObjectId(documento_id)})
                if resultado.deleted_count:
                    registrar_operacion(session['nombre_usuario'], 'Eliminar', 'Poblaciones', documento_id)
                flash("Documento eliminado correctamente." if resultado.deleted_count else "No se encontró el documento a eliminar.", 'success' if resultado.deleted_count else 'error')


        elif action == 'Consultar':
            documento_id = request.form.get('_id')
            documento = collection.find_one({'_id': ObjectId(documento_id)})
            if documento:
                # Muestra solo el documento consultado
                return render_template('manage_poblaciones.html', documentos=[documento], modo='ver_todo')
            else:
                flash("No se encontró el documento.", 'error')

        elif action == 'Ver Todo':
            documentos = list(collection.find())
            return render_template('manage_poblaciones.html', documentos=documentos, modo='ver_todo')

        elif action == 'Salir':
            return redirect(url_for('index'))
            
    return render_template('manage_poblaciones.html', fields=document_fields if document_fields else {}, nombre_coleccion='Poblaciones')


'''
            # Verificamos que todos los campos requeridos estén presentes
            if all(key in documento for key in required_fields):
                resultado = collection.insert_one(documento)
                flash(f"Documento agregado con éxito, ID: {resultado.inserted_id}", 'success')
            else:
                flash("Debe llenar todos los campos requeridos.", 'error')

            # Debug: Imprimir los campos enviados y los requeridos
            print("Campos enviados:", documento)
            print("Campos requeridos que faltan:", [field for field in required_fields if field not in documento])

'''
#RECETAS

@app.route('/herencias/recetas', methods=['GET', 'POST'])
def manage_recetas():
    client = conectar_bd()
    if not client:
        flash('No se pudo conectar a la base de datos.', 'error')
        return redirect(url_for('manage_recetas'))
    
    db = client['herencias']
    collection = db['Recetas']
    
    document_fields = collection.find_one()  # Encuentra el primer documento en la colección.

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'Agregar':
            documento = {k: v for k, v in request.form.items() if k != 'action' and v.strip()}
            if document_fields and all(documento.get(key) for key in document_fields.keys() if key != '_id'):
                resultado = collection.insert_one(documento)
                if resultado.acknowledged:
                    registrar_operacion(session['nombre_usuario'], 'Agregar', 'Recetas', str(resultado.inserted_id))
                flash(f"Documento agregado con éxito, ID: {resultado.inserted_id}", 'success')
            else:
                flash("Debe llenar todos los campos requeridos.", 'error')

        elif action == 'Actualizar':
            documento_id = request.form.get('_id')
            cambios = {k: v for k, v in request.form.items() if k != 'action' and k != '_id' and request.form.get('update_' + k)}
            if documento_id and cambios:
                resultado = collection.update_one({'_id': ObjectId(documento_id)}, {'$set': cambios})
                if resultado.modified_count:
                    registrar_operacion(session['nombre_usuario'], 'Actualizar', 'Recetas', documento_id)
                flash("Documento actualizado correctamente." if resultado.modified_count else "No se actualizó ningún documento.", 'success' if resultado.modified_count else 'error')
            else:
                flash("Debe proporcionar un ID válido y seleccionar los campos a actualizar.", 'error')

        elif action == 'Eliminar':
            documento_id = request.form.get('_id')
            if documento_id:
                resultado = collection.delete_one({'_id': ObjectId(documento_id)})
                if resultado.deleted_count:
                    registrar_operacion(session['nombre_usuario'], 'Eliminar', 'Recetas', documento_id)
                flash("Documento eliminado correctamente." if resultado.deleted_count else "No se encontró el documento a eliminar.", 'success' if resultado.deleted_count else 'error')
            else:
                flash("Debe proporcionar un ID válido para eliminar.", 'error')

        elif action == 'Consultar':
            documento_id = request.form.get('_id')
            documento = collection.find_one({'_id': ObjectId(documento_id)})
            if documento:
                # Muestra solo el documento consultado
                return render_template('manage_recetas.html', documentos=[documento], modo='ver_todo')
            else:
                flash("No se encontró el documento.", 'error')

        elif action == 'Ver Todo':
            documentos = list(collection.find())
            return render_template('manage_recetas.html', documentos=documentos, modo='ver_todo')

        elif action == 'Salir':
            return redirect(url_for('index'))
            
    return render_template('manage_recetas.html', fields=document_fields if document_fields else {}, nombre_coleccion='Recetas')

#
# Registrar operaciones
# #


def registrar_operacion(usuario, operacion, coleccion, documento_id):
    client = conectar_bd()
    if not client:
        print('Error de conexión a la base de datos')
        return False
    
    db = client['herencias']
    collection = db['Operaciones']
    
    registro = {
        'usuario': usuario,
        'operacion': operacion,
        'coleccion': coleccion,
        'documento_id': documento_id,
        'fecha_hora': datetime.now()
    }
    collection.insert_one(registro)
    return True


#registro de usuarios 
# 
#

@app.route('/')
def index():
    if 'nombre_usuario' in session:
        return render_template('dashboard.html', nombre_usuario=session['nombre_usuario'])
    else:
        return redirect(url_for('login'))
    
"""
@app.route('/')
def dashboard_investigador():
    if 'nombre_usuario' in session:
        return render_template('dashboard2.html', nombre_usuario=session['nombre_usuario'])
    else:
        return redirect(url_for('login'))
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    client = conectar_bd()
    if not client:
        flash('Error de conexión a la base de datos', 'error')
        return render_template('login.html')

    db = client['herencias']
    collection = db['Usuarios']

    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        password = request.form['password']
        usuario = collection.find_one({"nombre_usuario": nombre_usuario})

        if usuario and check_password_hash(usuario['password'], password):
            session['nombre_usuario'] = usuario['nombre_usuario']
            session['tipo_usuario'] = usuario['tipo_usuario']
            session['grupo_indigena'] = usuario.get('grupo_indigena', None)
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña inválidos', 'error')
    return render_template('login.html')
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    client = conectar_bd()
    if not client:
        flash('Error de conexión a la base de datos', 'error')
        return render_template('login.html')

    db = client['herencias']
    collection = db['Usuarios']

    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        password = request.form['password']
        usuario = collection.find_one({"nombre_usuario": nombre_usuario})

        if usuario and check_password_hash(usuario['password'], password):
            session['nombre_usuario'] = usuario['nombre_usuario']
            session['tipo_usuario'] = usuario['tipo_usuario']
            session['grupo_indigena'] = usuario.get('grupo_indigena', None)
            
            # Diferenciar el dashboard según el tipo de usuario
            if session['tipo_usuario'] == 'investigador':
                return redirect(url_for('dashboard_investigador'))  # Asume que tienes una función vista llamada dashboard_investigador
            else:
                return redirect(url_for('index'))  # Para otros tipos de usuarios
            
        else:
            flash('Usuario o contraseña inválidos', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    client = conectar_bd()
    if not client:
        flash('Error de conexión a la base de datos', 'error')
        return render_template('register.html')

    db = client['herencias']
    collection = db['Usuarios']

    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        password = request.form['password']
        tipo_usuario = request.form['tipo_usuario']
        grupo_indigena = request.form.get('grupo_indigena', None)  # None si no está presente

        if collection.find_one({'nombre_usuario': nombre_usuario}):
            flash('El nombre de usuario ya existe', 'error')
            return redirect(url_for('register'))

        nuevo_usuario = {
            'nombre_usuario': nombre_usuario,
            'password': generate_password_hash(password),
            'tipo_usuario': tipo_usuario,
            'grupo_indigena': grupo_indigena
        }
        collection.insert_one(nuevo_usuario)
        flash('Usuario registrado correctamente', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente')
    return redirect(url_for('login'))


##Implementación de fucniones de Investigador:

@app.route('/dashboard_investigador')
def dashboard_investigador():
    # Verifica si hay un usuario en sesión
    if 'nombre_usuario' in session:
        # Verifica si el tipo de usuario es investigador
        if session.get('tipo_usuario') == 'investigador':
            return render_template('dashboard2.html', nombre_usuario=session['nombre_usuario'])
        else:
            flash('Acceso restringido solo para investigadores.', 'error')
            return redirect(url_for('index'))  # Redirecciona al dashboard principal o a alguna otra vista adecuada
    else:
        flash('Por favor inicie sesión para acceder a esta página.', 'error')
        return redirect(url_for('login'))  # Redirecciona a la página de inicio de sesión si no hay usuario en sesión



if __name__ == '__main__':
    app.run(debug=True)