import logging
import board
import busio
from adafruit_mcp230xx.mcp23017 import MCP23017
from core.constants import UNPLUGGED_MODE
from result import Err, Ok, Result

logger = logging.getLogger("django")
if not UNPLUGGED_MODE:
    # Initialisation du bus I2C
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        mcp = MCP23017(i2c)
    # Le pilotage des périphériques sur la carte se fait via le protocole I2C.
    # En cas de problème de communication avec le bus I2C, une exception de type ValueError peut être levée, par exemple :
    # "ValueError : No I2C device at address: 0x20" indique qu'aucun périphérique I2C n'a été trouvé à l'adresse spécifiée.
    except ValueError as e:
        logger.error(f"Erreur d'initialisation I2C: {e}")
        i2c = None
        mcp = None


def set_mcp23017_pin_state(pin_number: int, state: bool) -> Result[bool, str]:
    if mcp is None:
        return Err("MCP23017 non initialisé")
    if i2c is None:
        return Err("I2C non initialisé")

    try:
        mcp_pin = mcp.get_pin(pin_number)
        # not state parce que la carte de contrôle coupe le chauffage quand le pin est à True
        mcp_pin.switch_to_output(value=not state)
        # Vérifie que l'état a bien été appliqué
        mcp_pin = mcp.get_pin(pin_number)
        return Ok(not mcp_pin.value)
    except ValueError as e:
        return Err(e)
