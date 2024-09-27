from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

app = Flask(__name__)
app.secret_key = 'tu_super_secreto'
app.config['SESSION_TYPE'] = 'filesystem'

# Lista para guardar usuarios
usuarios = []

def conectar_bd():
    uri = "mongodb://localhost:27017/"
    try:
        cliente = MongoClient(uri)
        cliente.admin.command('ping')  # Hacemos un ping para verificar la conexión
        return cliente
    except ConnectionFailure as e:
        print(f"Error al conectar a la base de datos MongoDB: {e}")
        return None

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

if __name__ == '__main__':
    app.run(debug=True)
