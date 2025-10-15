from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/promociones')
def promociones():
    return render_template('promociones.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/carrito')
def carrito():
    return render_template('carrito.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/registro')
def registro():
    return render_template('registro.html')


if __name__ == '__main__':
    app.run(debug=True)
