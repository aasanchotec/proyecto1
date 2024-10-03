from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
from bson.errors import InvalidId
from conectarBD import conectar_bd

app = Flask(__name__)
app.secret_key = 'tu_super_secreto'
app.config['SESSION_TYPE'] = 'filesystem'

# Lista para guardar usuarios
usuarios = []


# Lista para guardar usuarios
usuarios = [{
    'nombre_usuario': 'admin',
    'password': generate_password_hash('admin123'),
    'tipo_usuario': 'admin',
    'grupo_indigena': 'Bribri'
}]

@app.route('/')
def index():
    if 'nombre_usuario' in session:
        # Mensaje de bienvenida y opciones de colección
        return render_template('dashboard.html', nombre_usuario=session['nombre_usuario'], grupo_indigena=session.get('grupo_indigena', 'N/A'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        password = request.form['password']
        usuario = next((u for u in usuarios if u['nombre_usuario'] == nombre_usuario), None)
        if usuario and check_password_hash(usuario['password'], password):
            session['nombre_usuario'] = usuario['nombre_usuario']
            session['tipo_usuario'] = usuario['tipo_usuario']
            session['grupo_indigena'] = usuario['grupo_indigena']
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña inválidos', 'error')
    return render_template('login.html')


'''
## FUnciones de Login y regustrarse
@app.route('/')
def index():
    if 'nombre_usuario' in session:
        # Mensaje de bienvenida y opciones de colección
        return render_template('dashboard.html', nombre_usuario=session['nombre_usuario'])
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        password = request.form['password']
        for usuario in usuarios:
            if usuario['nombre_usuario'] == nombre_usuario and check_password_hash(usuario['password'], password):
                session['nombre_usuario'] = usuario['nombre_usuario']
                session['tipo_usuario'] = usuario['tipo_usuario']
                return redirect(url_for('index'))
        flash('Usuario o contraseña inválidos')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        password = request.form['password']
        tipo_usuario = request.form['tipo_usuario']

        # Verificar si el usuario ya existe
        for usuario in usuarios:
            if usuario['nombre_usuario'] == nombre_usuario:
                flash('El nombre de usuario ya existe')
                return redirect(url_for('register'))

        # Guardar el nuevo usuario
        usuarios.append({
            'nombre_usuario': nombre_usuario,
            'password': generate_password_hash(password),
            'tipo_usuario': tipo_usuario
        })
        flash('Usuario registrado correctamente')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('nombre_usuario', None)
    flash('Sesión cerrada')
    return redirect(url_for('login'))


'''
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        password = request.form['password']
        tipo_usuario = request.form['tipo_usuario']
        grupo_indigena = request.form.get('grupo_indigena')  # Asumiendo que se añade este campo al formulario

        # Verificar si el usuario ya existe
        usuario_existente = next((u for u in usuarios if u['nombre_usuario'] == nombre_usuario), None)
        if usuario_existente:
            flash('El nombre de usuario ya existe', 'error')
            return redirect(url_for('register'))

        # Guardar el nuevo usuario si no existe
        if nombre_usuario and password and tipo_usuario and grupo_indigena:  # Asegurar que todos los campos necesarios estén presentes
            nuevo_usuario = {
                'nombre_usuario': nombre_usuario,
                'password': generate_password_hash(password),
                'tipo_usuario': tipo_usuario,
                'grupo_indigena': grupo_indigena
            }
            usuarios.append(nuevo_usuario)
            flash('Usuario registrado correctamente', 'success')
            return redirect(url_for('login'))
        else:
            flash('Todos los campos son obligatorios', 'error')

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('nombre_usuario', None)
    session.pop('tipo_usuario', None)
    session.pop('grupo_indigena', None)
    flash('Sesión cerrada correctamente')
    return redirect(url_for('login'))

#MAnejo de colleciones 

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


'''
@app.route('/festividades', methods=['GET', 'POST'])
def manage_festividades():
    db = conectar_bd()
    collection = db['festividades']
    
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'Agregar':
            # Crea un documento a partir de los campos del formulario, excluyendo 'action' y el ID (el ID es auto-generado por MongoDB)
            documento = {
                'nombre_original': request.form.get('nombre_original', '').strip(),
                'fecha': request.form.get('fecha', '').strip(),
                'actividades': request.form.get('actividades', '').strip(),
                'quien_puede_asistir': request.form.get('quien_puede_asistir', '').strip(),
                'implicaciones': request.form.get('implicaciones', '').strip()
            }

            # Verifica que todos los campos requeridos estén completos
            if all(documento.values()):
                resultado = collection.insert_one(documento)
                flash(f"Documento agregado con éxito, ID: {resultado.inserted_id}", 'success')
            else:
                flash("Debe llenar todos los campos requeridos.", 'error')
        elif action == 'Actualizar':
            documento_id = request.form.get('_id')
            cambios = {k: v for k, v in request.form.items() if k != 'action' and k != '_id' and request.form.get('check_' + k)}
            if documento_id and cambios:
                resultado = collection.update_one({'_id': ObjectId(documento_id)}, {'$set': cambios})
                flash("Documento actualizado correctamente." if resultado.modified_count else "No se actualizó ningún documento.", 'success' if resultado.modified_count else 'error')
            else:
                flash("Debe proporcionar un ID válido y seleccionar los campos a actualizar.", 'error')

        elif action == 'Eliminar':
            documento_id = request.form.get('_id')
            if documento_id:
                resultado = collection.delete_one({'_id': ObjectId(documento_id)})
                flash("Documento eliminado correctamente." if resultado.deleted_count else "No se encontró el documento a eliminar.", 'success' if resultado.deleted_count else 'error')
            else:
                flash("Debe proporcionar un ID válido para eliminar.", 'error')

        elif action == 'Consultar':
            documento_id = request.form.get('_id')
            documento = collection.find_one({'_id': ObjectId(documento_id)}) if documento_id else None
            if documento:
                return render_template('manage_festividades.html', documento=documento)
            else:
                flash("No se encontró el documento.", 'error')

        elif action == 'Ver Todo':
            documentos = list(collection.find())
            return render_template('manage_festividades.html', documentos=documentos, modo='ver_todo')

        elif action == 'Salir':
            return redirect(url_for('index'))
            
    return render_template('manage_festividades.html', fields=document_fields if document_fields else {}, nombre_coleccion='Festividades')
'''

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
            documento = {k: v for k, v in request.form.items() if k != 'action' and v.strip()}
            if document_fields and all(documento.get(key) for key in document_fields.keys() if key != '_id'):
                resultado = collection.insert_one(documento)
                flash(f"Documento agregado con éxito, ID: {resultado.inserted_id}", 'success')
            else:
                flash("Debe llenar todos los campos requeridos.", 'error')

        elif action == 'Actualizar':
            documento_id = request.form.get('_id')
            cambios = {k: v for k, v in request.form.items() if k != 'action' and k != '_id' and request.form.get('update_' + k)}
            if documento_id and cambios:
                resultado = collection.update_one({'_id': ObjectId(documento_id)}, {'$set': cambios})
                flash("Documento actualizado correctamente." if resultado.modified_count else "No se actualizó ningún documento.", 'success' if resultado.modified_count else 'error')
            else:
                flash("Debe proporcionar un ID válido y seleccionar los campos a actualizar.", 'error')

        elif action == 'Eliminar':
            documento_id = request.form.get('_id')
            if documento_id:
                resultado = collection.delete_one({'_id': ObjectId(documento_id)})
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
                flash(f"Documento agregado con éxito, ID: {resultado.inserted_id}", 'success')
            else:
                flash("Debe llenar todos los campos requeridos.", 'error')

        elif action == 'Actualizar':
            documento_id = request.form.get('_id')
            cambios = {k: v for k, v in request.form.items() if k != 'action' and k != '_id' and request.form.get('update_' + k)}
            if documento_id and cambios:
                resultado = collection.update_one({'_id': ObjectId(documento_id)}, {'$set': cambios})
                flash("Documento actualizado correctamente." if resultado.modified_count else "No se actualizó ningún documento.", 'success' if resultado.modified_count else 'error')
            else:
                flash("Debe proporcionar un ID válido y seleccionar los campos a actualizar.", 'error')

        elif action == 'Eliminar':
            documento_id = request.form.get('_id')
            if documento_id:
                resultado = collection.delete_one({'_id': ObjectId(documento_id)})
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
            # Recolectamos todos los campos del formulario excepto 'action' y '_id'
            documento = {k: v for k, v in request.form.items() if k != 'action' and k != '_id' and v.strip()}
            required_fields = [key for key in document_fields if key != '_id' and document_fields[key]]

            

            # Verificamos que todos los campos requeridos estén presentes
            if all(key in documento for key in required_fields):
                resultado = collection.insert_one(documento)
                flash(f"Documento agregado con éxito, ID: {resultado.inserted_id}", 'success')
            else:
                flash("Debe llenar todos los campos requeridos.", 'error')

            # Debug: Imprimir los campos enviados y los requeridos
            print("Campos enviados:", documento)
            print("Campos requeridos que faltan:", [field for field in required_fields if field not in documento])

            
        elif action == 'Actualizar':
            documento_id = request.form.get('_id')
            cambios = {k: v for k, v in request.form.items() if k != 'action' and k != '_id' and request.form.get('update_' + k)}
            if documento_id and cambios:
                resultado = collection.update_one({'_id': ObjectId(documento_id)}, {'$set': cambios})
                flash("Documento actualizado correctamente." if resultado.modified_count else "No se actualizó ningún documento.", 'success' if resultado.modified_count else 'error')
            else:
                flash("Debe proporcionar un ID válido y seleccionar los campos a actualizar.", 'error')

        elif action == 'Eliminar':
            documento_id = request.form.get('_id')
            if documento_id:
                resultado = collection.delete_one({'_id': ObjectId(documento_id)})
                flash("Documento eliminado correctamente." if resultado.deleted_count else "No se encontró el documento a eliminar.", 'success' if resultado.deleted_count else 'error')
            else:
                flash("Debe proporcionar un ID válido para eliminar.", 'error')

        elif action == 'Consultar':
            documento_id = request.form.get('_id')
            documento = collection.find_one({'_id': ObjectId(documento_id)}) if documento_id else None
            if documento:
                return render_template('manage_poblaciones.html', documento=documento)
            else:
                flash("No se encontró el documento.", 'error')

        elif action == 'Ver Todo':
            documentos = list(collection.find())
            return render_template('manage_poblaciones.html', documentos=documentos, modo='ver_todo')
        


        elif action == 'Salir':
            return redirect(url_for('index'))
            
    return render_template('manage_poblaciones.html', fields=document_fields if document_fields else {}, nombre_coleccion='Poblaciones')

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
                flash(f"Documento agregado con éxito, ID: {resultado.inserted_id}", 'success')
            else:
                flash("Debe llenar todos los campos requeridos.", 'error')

        elif action == 'Actualizar':
            documento_id = request.form.get('_id')
            cambios = {k: v for k, v in request.form.items() if k != 'action' and k != '_id' and request.form.get('update_' + k)}
            if documento_id and cambios:
                resultado = collection.update_one({'_id': ObjectId(documento_id)}, {'$set': cambios})
                flash("Documento actualizado correctamente." if resultado.modified_count else "No se actualizó ningún documento.", 'success' if resultado.modified_count else 'error')
            else:
                flash("Debe proporcionar un ID válido y seleccionar los campos a actualizar.", 'error')

        elif action == 'Eliminar':
            documento_id = request.form.get('_id')
            if documento_id:
                resultado = collection.delete_one({'_id': ObjectId(documento_id)})
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


if __name__ == '__main__':
    app.run(debug=True)


