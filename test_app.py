import unittest
from app import app


class CrazyPriceTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True


    # Página principal
    def test_inicio(self):
        respuesta = self.app.get("/")
        self.assertEqual(respuesta.status_code, 200)


    # Página login
    def test_pagina_login(self):
        respuesta = self.app.get("/login")
        self.assertEqual(respuesta.status_code, 200)


    # Página registro
    def test_pagina_registro(self):
        respuesta = self.app.get("/registro")
        self.assertEqual(respuesta.status_code, 200)


    # Login incorrecto
    def test_login_incorrecto(self):
        respuesta = self.app.post("/login", data={
            "usuario": "xxxx",
            "password": "xxxx"
        })

        self.assertIn(
            b"Usuario o contrase",
            respuesta.data
        )


    # Registro nuevo usuario
    def test_registro_usuario(self):

        respuesta = self.app.post("/registro", data={
            "nombre": "Prueba",
            "usuario": "usuario_prueba123",
            "password": "123456"
        }, follow_redirects=True)

        self.assertEqual(respuesta.status_code, 200)


    # Intentar entrar al admin sin login
    def test_admin_sin_login(self):

        respuesta = self.app.get("/admin")

        self.assertEqual(
            respuesta.status_code,
            302
        )


    # Intentar entrar al cliente sin login
    def test_cliente_sin_login(self):

        respuesta = self.app.get("/cliente")

        self.assertEqual(
            respuesta.status_code,
            302
        )


    # Cerrar sesión
    def test_logout(self):

        respuesta = self.app.get(
            "/logout",
            follow_redirects=True
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )


if __name__ == "__main__":
    unittest.main()