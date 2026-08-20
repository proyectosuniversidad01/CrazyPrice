import unittest

from app import app


class CrazyPriceTest(unittest.TestCase):

    def setUp(self):

        self.app = app.test_client()

        self.app.testing = True


    # ==========================
    # PÁGINA PRINCIPAL
    # ==========================

    def test_inicio(self):

        respuesta = self.app.get("/")

        self.assertEqual(
            respuesta.status_code,
            200
        )


    # ==========================
    # PÁGINA LOGIN
    # ==========================

    def test_pagina_login(self):

        respuesta = self.app.get("/login")

        self.assertEqual(
            respuesta.status_code,
            200
        )


    # ==========================
    # PÁGINA REGISTRO
    # ==========================

    def test_pagina_registro(self):

        respuesta = self.app.get("/registro")

        self.assertEqual(
            respuesta.status_code,
            200
        )


    # ==========================
    # LOGIN INCORRECTO
    # ==========================

    def test_login_incorrecto(self):

        respuesta = self.app.post(
            "/login",
            data={
                "usuario": "xxxx",
                "password": "xxxx"
            }
        )

        self.assertIn(
            b"Usuario o contrase",
            respuesta.data
        )


    # ==========================
    # REGISTRO NUEVO USUARIO
    # ==========================

    def test_registro_usuario(self):

        respuesta = self.app.post(
            "/registro",
            data={
                "nombre": "Usuario Prueba",
                "usuario": "usuario_prueba123",
                "password": "123456"
            },
            follow_redirects=True
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )


    # ==========================
    # ADMIN SIN LOGIN
    # ==========================

    def test_admin_sin_login(self):

        respuesta = self.app.get(
            "/admin"
        )

        self.assertEqual(
            respuesta.status_code,
            302
        )


    # ==========================
    # CLIENTE SIN LOGIN
    # ==========================

    def test_cliente_sin_login(self):

        respuesta = self.app.get(
            "/cliente"
        )

        self.assertEqual(
            respuesta.status_code,
            302
        )


    # ==========================
    # PRODUCTOS SIN LOGIN
    # ==========================

    def test_producto_sin_login(self):

        respuesta = self.app.get(
            "/producto/1"
        )

        self.assertEqual(
            respuesta.status_code,
            302
        )


    # ==========================
    # CATEGORÍA SIN LOGIN
    # ==========================

    def test_genero_sin_login(self):

        respuesta = self.app.get(
            "/cliente/Caballero"
        )

        self.assertEqual(
            respuesta.status_code,
            302
        )


    # ==========================
    # CATEGORÍA INVÁLIDA
    # ==========================

    def test_genero_invalido(self):

        with self.app.session_transaction() as session:

            session["usuario"] = "cliente"

            session["rol"] = "cliente"


        respuesta = self.app.get(
            "/cliente/otra_categoria"
        )

        self.assertEqual(
            respuesta.status_code,
            302
        )


    # ==========================
    # CERRAR SESIÓN
    # ==========================

    def test_logout(self):

        respuesta = self.app.get(
            "/logout",
            follow_redirects=True
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )


    # ==========================
    # CLIENTE AUTENTICADO
    # ==========================

    def test_cliente_autenticado(self):

        with self.app.session_transaction() as session:

            session["usuario"] = "cliente"

            session["rol"] = "cliente"


        respuesta = self.app.get(
            "/cliente"
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )


    # ==========================
    # ADMIN AUTENTICADO
    # ==========================

    def test_admin_autenticado(self):

        with self.app.session_transaction() as session:

            session["usuario"] = "admin"

            session["rol"] = "admin"


        respuesta = self.app.get(
            "/admin"
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )


    # ==========================
    # CATEGORÍA CABALLERO
    # ==========================

    def test_categoria_caballero(self):

        with self.app.session_transaction() as session:

            session["usuario"] = "cliente"

            session["rol"] = "cliente"


        respuesta = self.app.get(
            "/cliente/Caballero"
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )


    # ==========================
    # CATEGORÍA DAMA
    # ==========================

    def test_categoria_dama(self):

        with self.app.session_transaction() as session:

            session["usuario"] = "cliente"

            session["rol"] = "cliente"


        respuesta = self.app.get(
            "/cliente/Dama"
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )


    # ==========================
    # CATEGORÍA NIÑO
    # ==========================

    def test_categoria_nino(self):

        with self.app.session_transaction() as session:

            session["usuario"] = "cliente"

            session["rol"] = "cliente"


        respuesta = self.app.get(
            "/cliente/Niño"
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )


    # ==========================
    # CATEGORÍA NIÑA
    # ==========================

    def test_categoria_nina(self):

        with self.app.session_transaction() as session:

            session["usuario"] = "cliente"

            session["rol"] = "cliente"


        respuesta = self.app.get(
            "/cliente/Niña"
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )


# ==========================
# EJECUTAR PRUEBAS
# ==========================

if __name__ == "__main__":
    unittest.main(verbosity=2)