from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64
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
    usuarios_collection = db['Usuarios']
    poblaciones_collection = db['Poblaciones']

    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        password = request.form['password']
        tipo_usuario = request.form['tipo_usuario']
        grupo_indigena = request.form.get('grupo_indigena')  # Asumiendo que se añade este campo al formulario

        if usuarios_collection.find_one({'nombre_usuario': nombre_usuario}):
            flash('El nombre de usuario ya existe', 'error')
            return redirect(url_for('register'))

        # Buscar grupo indígena para obtener idiomas hablados
        grupo = poblaciones_collection.find_one({'name': grupo_indigena})
        idiomas_hablados = grupo.get('languages_spoken', []) if grupo else []

        nuevo_usuario = {
            'nombre_usuario': nombre_usuario,
            'password': generate_password_hash(password),
            'tipo_usuario': tipo_usuario,
            'grupo_indigena': grupo_indigena,
            'idioma_hablado': ', '.join(idiomas_hablados)  # Join idiomas como string si hay varios
        }

        usuarios_collection.insert_one(nuevo_usuario)
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
    # Asegurarse de que solo los investigadores puedan acceder a esta vista
    if 'tipo_usuario' in session and session['tipo_usuario'] == 'investigador':
        return render_template('dashboard2.html', nombre_usuario=session['nombre_usuario'])
    else:
        flash('Acceso denegado: solo disponible para investigadores.', 'error')
        return redirect(url_for('login'))

@app.route('/')
def index_investigador():
    if 'nombre_usuario' in session:
        return render_template('dashboard2.html', nombre_usuario=session['nombre_usuario'])
    else:
        return redirect(url_for('login'))
    

@app.route('/resumen_general')
def resumen_general():
    # Añade aquí la lógica para obtener los datos necesarios para el resumen general
    return render_template('resumen_general.html')


@app.route('/estado_productos', methods=['GET', 'POST'])
def estado_productos():
    plot_url = None
    client = conectar_bd()
    if not client:
        flash('No se pudo conectar a la base de datos.', 'error')
        return render_template('mostrar_grafico.html')

    db = client['herencias']
    recetas_collection = db['Recetas']

    if request.method == 'POST':
        receta_id = request.form.get('receta_id')
        if not receta_id:
            flash('No se proporcionó el ID de la receta.', 'error')
            return render_template('mostrar_grafico.html')

        receta = recetas_collection.find_one({'_id': ObjectId(receta_id)})
        if not receta:
            flash('Receta no encontrada.', 'error')
            return render_template('mostrar_grafico.html')

        ingredientes = receta.get('ingredients', [])
        if not ingredientes:
            flash('No hay ingredientes para esta receta.', 'error')
            return render_template('mostrar_grafico.html')

        # Preparar datos para el gráfico
        nombres = [ing['name_spanish'] for ing in ingredientes]  # Ajustar según tus campos
        cantidades = [parse_quantity(ing['quantity']) for ing in ingredientes]  # Convertir todas las cantidades a un valor numérico estándar

        # Crear un gráfico de pastel
        fig, ax = plt.subplots()
        ax.pie(cantidades, labels=nombres, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Asegurar que se dibuje como un círculo

        # Convertir el gráfico a imagen PNG y codificarlo en base64
        img = BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')
        plt.close(fig)  # Cerrar la figura para liberar memoria

    return render_template('mostrar_grafico.html', plot_url=plot_url)

def parse_quantity(quantity_str):
    """ Función auxiliar para convertir las cantidades a un valor numérico estándar, asumiendo que la cantidad viene en un formato como '5 kg' o '200 g' """
    number, unit = quantity_str.split()
    number = float(number)  # Convertir el número a float
    # Normalizar unidades si es necesario, por ejemplo convertir todo a gramos
    if 'kg' in unit:
        return number * 1000
    elif 'g' in unit:
        return number
    elif 'litros' in unit:
        return number * 1000  # Asimilando litros a mililitros para unificación
    return number

















@app.route('/actividad_recetas')
def actividad_recetas():
    # código para manejar la ruta
    return render_template('dashboard2.html')



######## Administrar colaboradores

@app.route('/administrar_colaboradores', methods=['GET', 'POST'])
def administrar_colaboradores():
    client = conectar_bd()
    if not client:
        flash('No se pudo conectar a la base de datos.', 'error')
        return redirect(url_for('administrar_colaboradores'))
    
    db = client['herencias']
    collection = db['Usuarios']
    
    document_fields = collection.find_one()

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'Agregar':
            tipo_usuario = request.form.get('tipo_usuario', '').strip()
            if tipo_usuario == 'colaborador':
                documento = {
                    'nombre_usuario': request.form.get('nombre_usuario', '').strip(),
                    'password': generate_password_hash(request.form.get('password', '').strip()),
                    'tipo_usuario': tipo_usuario,
                    'grupo_indigena': request.form.get('grupo_indigena', '').strip(),
                    'idioma_hablado': request.form.get('idioma_hablado', '').strip()
                }
                if all(documento.values()):
                    resultado = collection.insert_one(documento)
                    flash(f"Usuario agregado con éxito, ID: {resultado.inserted_id}", 'success')
                else:
                    flash("Debe llenar todos los campos requeridos.", 'error')
            else:
                flash("Solo se pueden agregar usuarios colaboradores.", 'error')

        elif action in ['Actualizar', 'Eliminar', 'Consultar']:
            documento_id = request.form.get('_id')
            documento_actual = collection.find_one({'_id': ObjectId(documento_id)})
            
            if documento_actual and documento_actual.get('tipo_usuario') == 'colaborador':
                if action == 'Actualizar':
                    cambios = {k: v.strip() for k, v in request.form.items() if k not in ['action', '_id', 'update_password'] and request.form.get('update_' + k)}
                    if 'update_password' in request.form:
                        cambios['password'] = generate_password_hash(request.form.get('password').strip())
                    resultado = collection.update_one({'_id': ObjectId(documento_id)}, {'$set': cambios})
                    flash("Usuario actualizado correctamente." if resultado.modified_count else "No se actualizó ningún usuario.", 'success' if resultado.modified_count else 'error')
                
                elif action == 'Eliminar':
                    resultado = collection.delete_one({'_id': ObjectId(documento_id)})
                    flash("Usuario eliminado correctamente." if resultado.deleted_count else "No se encontró el usuario a eliminar.", 'success' if resultado.deleted_count else 'error')
                
                elif action == 'Consultar':
                    return render_template('gestion_usuarios.html', documentos=[documento_actual], modo='ver_todo')
            else:
                flash("Operación permitida solo para usuarios colaboradores.", 'error')

        elif action == 'Ver Todo':
            documentos = list(collection.find({'tipo_usuario': 'colaborador'}))
            return render_template('gestion_usuarios.html', documentos=documentos, modo='ver_todo')

        elif action == 'Salir':
            return redirect(url_for('dashboard_investigador'))

    return render_template('gestion_usuarios.html', fields=document_fields if document_fields else {}, nombre_coleccion='Usuarios')

    
@app.route('/consultar_receta', methods=['GET', 'POST'])
def consultar_receta():
    db = conectar_bd()
    if not db:
        flash('No se pudo conectar a la base de datos.', 'error')
        return redirect(url_for('login'))

    if 'nombre_usuario' in session:
        recetas = db['Recetas'].find({'creado_por': session['nombre_usuario']})
        return render_template('ver_recetas.html', recetas=recetas)
    else:
        flash('No autorizado', 'error')
        return redirect(url_for('login'))



@app.route('/consultar_ingredientes_usuario', methods=['POST'])
def consultar_ingredientes_usuario():
    client = conectar_bd()
    if not client:
        flash('No se pudo conectar a la base de datos.', 'error')
        return redirect(url_for('administrar_colaboradores'))
    
    db = client['herencias']
    operaciones_collection = db['Operaciones']
    ingredientes_collection = db['Ingredientes']

    usuario = request.form.get('usuario')
    if not usuario:
        flash('No se proporcionó el nombre de usuario.', 'error')
        return redirect(url_for('administrar_colaboradores'))

    # Obtener operaciones de adición en la colección Ingredientes por el usuario
    operaciones = operaciones_collection.find({
        'usuario': usuario,
        'coleccion': 'Ingredientes',
        'operacion': 'Agregar'
    })

    # Recuperar los IDs de los ingredientes que el usuario ha agregado
    ingrediente_ids = [ObjectId(op['documento_id']) for op in operaciones if 'documento_id' in op]
    print(f"Ingredient IDs retrieved: {ingrediente_ids}")  # Depuración

    # Buscar los ingredientes específicos por ID
    ingredientes = ingredientes_collection.find({
        '_id': {'$in': ingrediente_ids}
    })

    # Preparar los ingredientes para pasar a la plantilla
    ingredientes_lista = list(ingredientes)
    print(f"Ingredients found: {ingredientes_lista}")  # Depuración para ver qué se recupera exactamente

    if ingredientes_lista:
        return render_template('gestion_usuarios.html', ingredientes=ingredientes_lista)
    else:
        flash('No se encontraron ingredientes agregados por este usuario.', 'info')
        return render_template('gestion_usuarios.html')

@app.route('/top_cinco', methods=['GET'])
def top_cinco():
    client = conectar_bd()
    if not client:
        flash('No se pudo conectar a la base de datos.', 'error')
        return redirect(url_for('administrar_colaboradores'))
    
    db = client['herencias']
    collection = db['Operaciones']

    collection.create_index([('usuario', ASCENDING)])

    top_usuarios = collection.aggregate([
        {"$group": {
            "_id": "$usuario",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ])

    top_usuarios = list(top_usuarios)  # Convertir cursor a lista para pasarlo al template

    # Asumimos que la plantilla puede manejar 'top_usuarios'
    return render_template('gestion_usuarios.html', top_usuarios=top_usuarios)


@app.route('/notificaciones_alertas')
def notificaciones_alertas():
    # Añade aquí la lógica para mostrar notificaciones y alertas relevantes
    return render_template('notificaciones_alertas.html')



if __name__ == '__main__':
    app.run(debug=True)