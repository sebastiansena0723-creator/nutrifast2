from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

# Base de datos de productos con precios actualizados
productos = [
    {
        "id": 1, 
        "nombre": "Arepa con jugo", 
        "precio": 8000, 
        "imagen": "arepa con jugo.jpg",
        "categoria": "desayuno", 
        "descripcion": "Arepa integral con jugo natural de naranja"
    },
    {
        "id": 2, 
        "nombre": "Bowl saludable", 
        "precio": 15000, 
        "imagen": "bowl.jpg",
        "categoria": "almuerzo", 
        "descripcion": "Bowl con quinoa, pollo y vegetales frescos"
    },
    {
        "id": 3, 
        "nombre": "Hamburguesa fit", 
        "precio": 18000, 
        "imagen": "hamburguesa 1.jpeg",
        "categoria": "cena", 
        "descripcion": "Hamburguesa de lentejas con pan integral"
    },
    {
        "id": 4, 
        "nombre": "Smoothie verde", 
        "precio": 7000, 
        "imagen": "smoothie.jpeg",
        "categoria": "bebida", 
        "descripcion": "Smoothie energético de espinaca y piña"
    },
    {
        "id": 5, 
        "nombre": "Hamburguesa clásica", 
        "precio": 20000, 
        "imagen": "hamburguesa 2.jpeg",
        "categoria": "cena", 
        "descripcion": "Hamburguesa artesanal con carne premium"
    },
    {
        "id": 6, 
        "nombre": "Arepa especial", 
        "precio": 12000, 
        "imagen": "arepa.jpeg",
        "categoria": "desayuno", 
        "descripcion": "Arepa rellena con queso, aguacate y huevo"
    }
]

# Usuarios de ejemplo
usuarios = {
    "admin@nutrifast.com": {"password": "admin123", "nombre": "Administrador"},
    "cliente@ejemplo.com": {"password": "cliente123", "nombre": "Cliente Ejemplo"}
}

@app.route('/')
def index():
    productos_destacados = [p for p in productos if p['id'] in [1, 2, 3]]
    return render_template('index.html', productos=productos_destacados)

@app.route('/menu')
def menu():
    categoria = request.args.get('categoria', 'todos')
    if categoria == 'todos':
        productos_filtrados = productos
    else:
        productos_filtrados = [p for p in productos if p['categoria'] == categoria]
    
    return render_template('menu.html', 
                         productos=productos_filtrados, 
                         categoria_actual=categoria)

@app.route('/promociones')
def promociones():
    return render_template('promociones.html')

@app.route('/portafolio')
def portafolio():
    return render_template('portafolio.html')

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        mensaje = request.form.get('mensaje')
        
        flash(f'¡Gracias {nombre}! Tu mensaje ha sido enviado.', 'success')
        return redirect(url_for('contacto'))
    
    return render_template('contacto.html')

@app.route('/carrito')
def carrito():
    carrito = session.get('carrito', [])
    total = sum(item['precio'] * item['cantidad'] for item in carrito)
    return render_template('carrito.html', carrito=carrito, total=total)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email in usuarios and usuarios[email]['password'] == password:
            session['usuario'] = {
                'email': email,
                'nombre': usuarios[email]['nombre']
            }
            session.permanent = True
            flash(f'¡Bienvenido {usuarios[email]["nombre"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Credenciales incorrectas', 'error')
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email in usuarios:
            flash('El email ya está registrado', 'error')
        else:
            usuarios[email] = {'password': password, 'nombre': nombre}
            flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
    
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('index'))

@app.route('/agregar', methods=['POST'])
def agregar():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para agregar productos al carrito', 'warning')
        return redirect(url_for('login'))
    
    id_producto = int(request.form['id'])
    producto = next((p for p in productos if p['id'] == id_producto), None)
    
    if producto:
        carrito = session.get('carrito', [])
        
        item_existente = next((item for item in carrito if item['id'] == id_producto), None)
        
        if item_existente:
            item_existente['cantidad'] += 1
        else:
            producto_con_cantidad = producto.copy()
            producto_con_cantidad['cantidad'] = 1
            carrito.append(producto_con_cantidad)
        
        session['carrito'] = carrito
        session.modified = True
        flash(f'¡{producto["nombre"]} agregado al carrito!', 'success')
    
    return redirect(request.referrer or url_for('menu'))

@app.route('/actualizar_carrito', methods=['POST'])
def actualizar_carrito():
    carrito = session.get('carrito', [])
    id_producto = int(request.form['id'])
    accion = request.form['accion']
    
    for item in carrito:
        if item['id'] == id_producto:
            if accion == 'incrementar':
                item['cantidad'] += 1
            elif accion == 'decrementar' and item['cantidad'] > 1:
                item['cantidad'] -= 1
            elif accion == 'eliminar':
                carrito.remove(item)
            break
    
    session['carrito'] = carrito
    session.modified = True
    return redirect(url_for('carrito'))

@app.route('/vaciar_carrito')
def vaciar_carrito():
    session['carrito'] = []
    session.modified = True
    flash('Carrito vaciado correctamente', 'info')
    return redirect(url_for('carrito'))

@app.route('/buscar')
def buscar():
    query = request.args.get('q', '').lower()
    if query:
        resultados = [p for p in productos 
                     if query in p['nombre'].lower() or query in p['descripcion'].lower()]
    else:
        resultados = []
    
    return render_template('buscar.html', resultados=resultados, query=query)

if __name__ == '__main__':
    app.run(debug=True)