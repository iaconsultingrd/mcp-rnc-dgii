"""Servidor MCP para consultar contribuyentes dominicanos (RNC / cédula)
usando el listado público de la DGII.

Uso:
    python server.py descargar   # baja DGII_RNC.zip y extrae el .TXT
    python server.py             # inicia el servidor MCP (stdio)
"""

import io
import os
import sys
import unicodedata
import urllib.request
import zipfile
from pathlib import Path

from mcp.server.mcpserver import MCPServer

URL_DGII = "https://dgii.gov.do/app/WebApps/Consultas/RNC/DGII_RNC.zip"
ARCHIVO = Path(os.environ.get("RNC_DGII_ARCHIVO", Path(__file__).parent / "datos" / "DGII_RNC.TXT"))


def normalizar(texto: str) -> str:
    """Minúsculas y sin acentos, para buscar sin importar cómo se escriba."""
    sin_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sin_acentos.lower().strip()


def solo_digitos(rnc: str) -> str:
    return "".join(c for c in rnc if c.isdigit())


def parsear_linea(linea: str) -> dict | None:
    """Cada línea del archivo es: RNC|RAZÓN SOCIAL|NOMBRE COMERCIAL|...otros campos."""
    campos = [c.strip() for c in linea.rstrip("\r\n").split("|")]
    if len(campos) < 3 or not solo_digitos(campos[0]):
        return None
    return {
        "rnc": campos[0],
        "razon_social": campos[1],
        "nombre_comercial": campos[2],
        "otros_campos": [c for c in campos[3:] if c],
    }


def cargar(ruta: Path) -> dict[str, dict]:
    """Carga el archivo de la DGII (latin-1) en un diccionario indexado por RNC."""
    registros = {}
    with open(ruta, encoding="latin-1") as f:
        for linea in f:
            registro = parsear_linea(linea)
            if registro:
                registros[solo_digitos(registro["rnc"])] = registro
    return registros


def descargar(destino: Path = ARCHIVO) -> None:
    print(f"Descargando {URL_DGII} ...")
    with urllib.request.urlopen(URL_DGII) as r:
        contenido = r.read()
    with zipfile.ZipFile(io.BytesIO(contenido)) as z:
        nombre_txt = next(n for n in z.namelist() if n.upper().endswith(".TXT"))
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(z.read(nombre_txt))
    print(f"Listo: {destino}")


_registros: dict[str, dict] | None = None


def registros() -> dict[str, dict]:
    global _registros
    if _registros is None:
        if not ARCHIVO.exists():
            raise FileNotFoundError(
                f"No encontré {ARCHIVO}. Ejecuta primero: python server.py descargar"
            )
        _registros = cargar(ARCHIVO)
    return _registros


def buscar_rnc(rnc: str) -> dict:
    return registros().get(solo_digitos(rnc)) or {"error": f"No se encontró el RNC {rnc}"}


def buscar_nombre(nombre: str, limite: int = 10) -> list[dict]:
    consulta = normalizar(nombre)
    resultados = []
    for r in registros().values():
        if consulta in normalizar(r["razon_social"]) or consulta in normalizar(r["nombre_comercial"]):
            resultados.append(r)
            if len(resultados) >= limite:
                break
    return resultados


servidor = MCPServer(
    "rnc-dgii",
    instructions="Consulta contribuyentes de República Dominicana con el listado público de la DGII.",
)


@servidor.tool()
def consultar_rnc(rnc: str) -> dict:
    """Busca un contribuyente dominicano por RNC (9 dígitos) o cédula (11 dígitos). Acepta guiones."""
    return buscar_rnc(rnc)


@servidor.tool()
def buscar_por_nombre(nombre: str, limite: int = 10) -> list[dict]:
    """Busca contribuyentes por razón social o nombre comercial (no distingue acentos ni mayúsculas)."""
    return buscar_nombre(nombre, limite)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "descargar":
        descargar()
    else:
        servidor.run()
