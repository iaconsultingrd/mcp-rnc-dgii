import tempfile
import unittest
from pathlib import Path

import server

MUESTRA = (
    "101000001|EMPRESA DE EJEMPLO SRL|EL EJEMPLO|COMERCIO|01/01/2000|ACTIVO|NORMAL\n"
    "40200000001|JOSÉ PÉREZ|  |SERVICIOS|  |ACTIVO|NORMAL\n"
    "linea invalida\n"
)


class TestServidor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ruta = Path(tempfile.mkdtemp()) / "DGII_RNC.TXT"
        ruta.write_text(MUESTRA, encoding="latin-1")
        server._registros = server.cargar(ruta)

    def test_carga_ignora_lineas_invalidas(self):
        self.assertEqual(len(server._registros), 2)

    def test_consultar_rnc_con_guiones(self):
        r = server.buscar_rnc("1-01-00000-1")
        self.assertEqual(r["razon_social"], "EMPRESA DE EJEMPLO SRL")
        self.assertIn("ACTIVO", r["otros_campos"])

    def test_rnc_inexistente(self):
        self.assertIn("error", server.buscar_rnc("999999999"))

    def test_buscar_sin_acentos(self):
        r = server.buscar_nombre("jose perez")
        self.assertEqual(r[0]["rnc"], "40200000001")

    def test_buscar_nombre_comercial(self):
        self.assertEqual(len(server.buscar_nombre("ejemplo")), 1)


if __name__ == "__main__":
    unittest.main()
