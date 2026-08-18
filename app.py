from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)

app.secret_key = "crazyprice_secret_key"


# ==========================
# CONFIGURACIÓN IMÁGENES
# ==========================

UPLOAD_FOLDER = "static/img"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB máximo


ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


def archivo_permitido(nombre):

    return "." in nombre and \
           nombre.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ==========================
# BASE DE DATOS
# ==========================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usuarios.db"

db = SQLAlchemy(app)



# ==========================
# MODELO USUARIO
# ==========================

class Usuario(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(100))

    usuario = db.Column(db.String(50), unique=True)

    password = db.Column(db.String(200))

    rol = db.Column(db.String(20))





# ==========================
# MODELO PEDIDO
# ==========================

class Pedido(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    cliente = db.Column(db.String(100))

    producto = db.Column(db.String(100))

    cantidad = db.Column(db.Integer)

    total = db.Column(db.Float)

    estado = db.Column(
        db.String(50),
        default="Pendiente"
    )

# ==========================
# MODELO PRODUCTO
# ==========================

class Producto(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(100))

    descripcion = db.Column(db.String(300))

    precio = db.Column(db.Float)

    stock = db.Column(db.Integer)

    imagen = db.Column(db.String(500))

    genero = db.Column(db.String(20))



# ==========================
# INICIO
# ==========================

@app.route("/")
def inicio():

    return render_template("index.html")





# ==========================
# REGISTRO CLIENTE
# ==========================

@app.route("/registro", methods=["GET","POST"])
def registro():


    if request.method == "POST":


        nombre = request.form["nombre"]

        usuario = request.form["usuario"]

        password = request.form["password"]



        existe = Usuario.query.filter_by(
            usuario=usuario
        ).first()



        if existe:

            return "El usuario ya existe"



        nuevo_usuario = Usuario(

            nombre=nombre,

            usuario=usuario,

            password=generate_password_hash(password),

            rol="cliente"

        )



        db.session.add(nuevo_usuario)

        db.session.commit()



        return redirect("/login")



    return render_template("registro.html")







# ==========================
# LOGIN
# ==========================

@app.route("/login", methods=["GET","POST"])
def login():


    if request.method == "POST":


        usuario = request.form["usuario"]

        password = request.form["password"]



        user = Usuario.query.filter_by(
            usuario=usuario
        ).first()



        if user and check_password_hash(
            user.password,
            password
        ):



            session["usuario"] = user.usuario

            session["rol"] = user.rol



            if user.rol == "admin":

                return redirect("/admin")


            else:

                return redirect("/cliente")



        return "Usuario o contraseña incorrectos"



    return render_template("login.html")








# ==========================
# PANEL ADMIN
# ==========================

@app.route("/admin")
def admin():

    if session.get("rol") != "admin":

        return redirect("/login")


    pedidos = Pedido.query.all()

    usuarios = Usuario.query.all()

    productos = Producto.query.all()


    facturacion = db.session.query(
        db.func.sum(Pedido.total)
    ).filter(
        Pedido.estado == "Entregado"
    ).scalar()


    if facturacion is None:

        facturacion = 0



    return render_template(
        "admin_dashboard.html",
        pedidos=pedidos,
        usuarios=usuarios,
        productos=productos,
        facturacion=facturacion
    )


@app.route("/admin/productos")
def admin_productos():

    if session.get("rol") != "admin":

        return redirect("/login")


    productos = Producto.query.all()


    return render_template(
        "admin_productos.html",
        productos=productos
    )


# ==========================
# AGREGAR PRODUCTO
# ==========================

@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():

    if session.get("rol") != "admin":

        return redirect("/login")


    imagen = request.form.get("imagen")


    archivo = request.files.get("archivo")


    # Si sube una imagen desde su PC
    if archivo and archivo.filename != "":


        if not archivo_permitido(archivo.filename):

            flash(
                "Formato de imagen no permitido. Use PNG, JPG, JPEG o WEBP",
                "error"
            )

            return redirect("/admin/productos")



        nombre_archivo = secure_filename(
            archivo.filename
        )



        ruta = os.path.join(
            app.config["UPLOAD_FOLDER"],
            nombre_archivo
        )



        archivo.save(ruta)



        imagen = "img/" + nombre_archivo





    nuevo_producto = Producto(

        nombre=request.form["nombre"],

        descripcion=request.form["descripcion"],

        precio=float(request.form["precio"]),

        stock=int(request.form["stock"]),

        imagen=imagen,

        genero=request.form["genero"]

     )



    db.session.add(nuevo_producto)

    db.session.commit()



    return redirect("/admin/productos")



# ==========================
# EDITAR PRODUCTO
# ==========================

@app.route("/editar_producto/<int:id>", methods=["GET","POST"])
def editar_producto(id):

    if session.get("rol") != "admin":

        return redirect("/login")


    producto = Producto.query.get_or_404(id)



    if request.method == "POST":


        producto.nombre = request.form["nombre"]

        producto.descripcion = request.form["descripcion"]

        producto.precio = float(request.form["precio"])

        producto.stock = int(request.form["stock"])

        producto.genero = request.form["genero"]



        # Imagen por URL

        imagen_url = request.form["imagen"]


        if imagen_url:

            producto.imagen = imagen_url



        # Imagen subida

        archivo = request.files.get("archivo")


        if archivo and archivo.filename:


            nombre_archivo = secure_filename(
                archivo.filename
            )


            archivo.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    nombre_archivo
                )
            )


            producto.imagen = "img/" + nombre_archivo



        db.session.commit()



        return redirect("/admin/productos")



    return render_template(
        "editar_producto.html",
        producto=producto
    )




# ==========================
# ELIMINAR PRODUCTO
# ==========================

@app.route("/eliminar_producto/<int:id>")
def eliminar_producto(id):

    if session.get("rol") != "admin":

        return redirect("/login")


    producto = Producto.query.get(id)


    if producto:

        db.session.delete(producto)

        db.session.commit()


    return redirect("/admin/productos")



@app.route("/admin/usuarios")
def admin_usuarios():

    if session.get("rol") != "admin":

        return redirect("/login")


    usuarios = Usuario.query.all()


    return render_template(
        "admin_usuarios.html",
        usuarios=usuarios
    )


@app.route("/admin/pedidos")
def admin_pedidos():

    if session.get("rol") != "admin":

        return redirect("/login")


    pedidos = Pedido.query.all()


    return render_template(
        "admin_pedidos.html",
        pedidos=pedidos
    )




# ==========================
# PANEL CLIENTE
# ==========================

@app.route("/cliente")
def cliente():

    if session.get("rol") != "cliente":

        return redirect("/login")


    productos = Producto.query.all()


    return render_template(
    "cliente.html",
    productos=productos,
    carrito=session.get("carrito", [])
    )




@app.route("/cliente/<genero>")
def productos_por_genero(genero):

    if session.get("rol") != "cliente":

        return redirect("/login")


    generos_validos = [
        "Caballero",
        "Dama",
        "Niño",
        "Niña"
    ]


    if genero not in generos_validos:

        return redirect("/cliente")


    productos = Producto.query.filter_by(
        genero=genero
    ).all()


    return render_template(
        "cliente.html",
        productos=productos,
        carrito=session.get("carrito", []),
        genero_actual=genero
    )






# ==========================
# VER PRODUCTO
# ==========================

@app.route("/producto/<int:id>")
def ver_producto(id):

    if session.get("rol") != "cliente":

        return redirect("/login")


    producto = Producto.query.get_or_404(id)


    carrito = session.get(
        "carrito",
        []
    )


    return render_template(

        "producto.html",

        producto=producto,

        carrito=carrito

    )




# ==========================
# AGREGAR AL CARRITO
# ==========================

# ==========================
# AGREGAR AL CARRITO
# ==========================

@app.route("/agregar_carrito", methods=["POST"])
def agregar_carrito():

    if session.get("rol") != "cliente":

        return redirect("/login")


    id_producto = int(request.form["id"])

    producto = request.form["producto"]

    precio = float(request.form["precio"])

    imagen = request.form["imagen"]

    cantidad = int(request.form["cantidad"])


    carrito = session.get("carrito", [])


    encontrado = False


    for item in carrito:

        if item["id"] == id_producto:

            item["cantidad"] += cantidad

            encontrado = True

            break


    if not encontrado:

        carrito.append({

            "id": id_producto,

            "producto": producto,

            "precio": precio,

            "cantidad": cantidad,

            "imagen": imagen

        })


    session["carrito"] = carrito


    # ==========================
    # REGRESAR AL LUGAR DE ORIGEN
    # ==========================

    origen = request.args.get("origen")

    genero = request.args.get("genero")


    if origen == "producto":

        return redirect(f"/producto/{id_producto}")


    if origen == "cliente" and genero:

        return redirect(f"/cliente/{genero}")


    return redirect("/cliente")


# ==========================
# VER CARRITO
# ==========================

@app.route("/carrito")
def carrito():

    if session.get("rol") != "cliente":

        return redirect("/login")


    carrito = session.get("carrito", [])


    total = 0


    for item in carrito:

        total += item["precio"] * item["cantidad"]


    return render_template(

        "carrito.html",

        carrito=carrito,

        total=total

    )



# ==========================
# ELIMINAR PRODUCTO
# ==========================

@app.route("/eliminar_carrito/<int:index>")
def eliminar_carrito(index):

    if session.get("rol") != "cliente":

        return redirect("/login")


    carrito = session.get("carrito", [])


    if index < len(carrito):

        carrito.pop(index)


    session["carrito"] = carrito


    return redirect("/carrito")



# ==========================
# VACIAR CARRITO
# ==========================

@app.route("/vaciar_carrito")
def vaciar_carrito():

    session["carrito"] = []

    return redirect("/carrito")



# ==========================
# CONFIRMAR COMPRA
# ==========================

@app.route("/confirmar_compra")
def confirmar_compra():

    if session.get("rol") != "cliente":

        return redirect("/login")


    carrito = session.get("carrito", [])


    if not carrito:

        return redirect("/carrito")



    # ==========================
    # BUSCAR USUARIO
    # ==========================

    usuario = Usuario.query.filter_by(
        usuario=session["usuario"]
    ).first()


    if not usuario:

        flash(
            "No se pudo identificar al usuario.",
            "error"
        )

        return redirect("/carrito")



    # ==========================
    # VALIDAR STOCK
    # ==========================

    for item in carrito:

        producto = Producto.query.get(item["id"])


        if not producto:

            flash(
                f"El producto {item['producto']} ya no existe.",
                "error"
            )

            return redirect("/carrito")


        if producto.stock < item["cantidad"]:

            flash(

                f"No hay suficiente stock para "
                f"{producto.nombre}. "
                f"Disponible: {producto.stock}",

                "error"

            )

            return redirect("/carrito")



    # ==========================
    # CREAR PEDIDOS Y RESTAR STOCK
    # ==========================

    for item in carrito:

        producto = Producto.query.get(item["id"])


        # Restar stock una sola vez

        producto.stock -= item["cantidad"]


        # Crear pedido

        nuevo_pedido = Pedido(

            cliente=usuario.nombre,

            producto=producto.nombre,

            cantidad=item["cantidad"],

            total=item["precio"] * item["cantidad"],

            estado="Pendiente"

        )


        db.session.add(nuevo_pedido)



    # Guardar cambios

    db.session.commit()


    # Vaciar carrito

    session["carrito"] = []


    flash(

        "Compra realizada correctamente.",

        "success"

    )


    return redirect("/cliente")



# ==========================
# CAMBIAR ESTADO PEDIDO
# ==========================

@app.route("/estado_pedido/<int:id>/<estado>")
def estado_pedido(id, estado):

    if session.get("rol") != "admin":
        return redirect("/login")

    pedido = Pedido.query.get_or_404(id)

    # Flujo permitido
    if pedido.estado == "Pendiente" and estado == "Procesando":

        pedido.estado = "Procesando"

    elif pedido.estado == "Procesando" and estado == "Enviado":

        pedido.estado = "Enviado"

    elif pedido.estado == "Enviado" and estado == "Entregado":

        pedido.estado = "Entregado"

    # Si intenta volver atrás o saltarse estados, no hace nada
    else:

        return redirect("/admin/pedidos")

    db.session.commit()

    return redirect("/admin/pedidos")








# ==========================
# CERRAR SESION
# ==========================

@app.route("/logout")
def logout():

    carrito = session.get("carrito", [])


    session.clear()


    if carrito:

        session["carrito"] = carrito


    return redirect("/login")







# ==========================
# CREAR BASE DE DATOS
# USUARIOS Y PRODUCTOS POR DEFECTO
# ==========================

with app.app_context():

    db.create_all()


    # ==========================
    # ADMIN POR DEFECTO
    # ==========================

    admin = Usuario.query.filter_by(
        usuario="admin"
    ).first()


    if not admin:

        admin = Usuario(

            nombre="Administrador",

            usuario="admin",

            password=generate_password_hash(
                "admin123"
            ),

            rol="admin"

        )

        db.session.add(admin)


    # ==========================
    # CLIENTE POR DEFECTO
    # ==========================

    cliente = Usuario.query.filter_by(
        usuario="cliente"
    ).first()


    if not cliente:

        cliente = Usuario(

            nombre="Cliente Demo",

            usuario="cliente",

            password=generate_password_hash(
                "cliente123"
            ),

            rol="cliente"

        )

        db.session.add(cliente)


    # ==========================
    # GUARDAR CAMBIOS
    # ==========================

    db.session.commit()




# ==========================
# PRODUCTOS POR DEFECTO
# ==========================

# ==========================
# PRODUCTOS POR DEFECTO
# ACTUALIZAR IMAGENES
# ==========================

with app.app_context():

    productos = Producto.query.all()


    for producto in productos:

        if producto.nombre == "Camisa Premium":

            producto.imagen = "img/camisa.jpg"


        elif producto.nombre == "Zapatillas Urban":

            producto.imagen = "img/zapatillas.jpg"


        elif producto.nombre == "Chaqueta Moderna":

            producto.imagen = "img/chaqueta.jpg"



    db.session.commit()






if __name__ == "__main__":

    app.run(debug=True)