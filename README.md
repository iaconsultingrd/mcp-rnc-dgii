# mcp-rnc-dgii 🇩🇴

Servidor [MCP](https://modelcontextprotocol.io) que le permite a Claude consultar contribuyentes de República Dominicana (RNC y cédula) usando el **listado público de la DGII**.

Con él puedes pedirle a Claude cosas como:

> "Verifica estos 20 RNC de proveedores y dime cuáles no aparecen en la DGII."
> "Busca el RNC de esta empresa por su nombre comercial."

Todo corre en tu computadora: los datos se descargan una vez desde la DGII y las consultas no salen a internet.

## Herramientas

| Herramienta | Qué hace |
| - | - |
| `consultar_rnc(rnc)` | Busca por RNC (9 dígitos) o cédula (11). Acepta guiones. |
| `buscar_por_nombre(nombre, limite)` | Busca por razón social o nombre comercial, sin importar acentos ni mayúsculas. |

Cada resultado trae `rnc`, `razon_social`, `nombre_comercial` y `otros_campos` (el resto de columnas del archivo tal como lo publica la DGII: actividad, fecha, estado, régimen, etc.).

## Instalación

```bash
git clone https://github.com/iaconsultingrd/mcp-rnc-dgii.git
cd mcp-rnc-dgii
pip install -r requirements.txt

# Descargar el listado de la DGII (repetir de vez en cuando para actualizarlo)
python server.py descargar
```

### Conectarlo a Claude Code

```bash
claude mcp add rnc-dgii -- python /ruta/completa/a/mcp-rnc-dgii/server.py
```

### Conectarlo a Claude Desktop

Agrega esto a la configuración de servidores MCP:

```json
{
  "mcpServers": {
    "rnc-dgii": {
      "command": "python",
      "args": ["/ruta/completa/a/mcp-rnc-dgii/server.py"]
    }
  }
}
```

Para usar un archivo en otra ubicación, define la variable `RNC_DGII_ARCHIVO`.

## Tests

```bash
python -m unittest
```

## Aviso

Proyecto comunitario, no oficial ni afiliado a la DGII. Los datos son los que la DGII publica; para trámites oficiales verifica siempre en [dgii.gov.do](https://dgii.gov.do).

---

Hecho con Claude Code por [Juan Navarro](https://www.linkedin.com/in/juandanielnavarro/) · Licencia MIT.
