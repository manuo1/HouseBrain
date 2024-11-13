from result import Err, Ok, Result
from teleinfo.constants import (
    FIRST_TELEINFO_FRAME_KEY,
    REQUIRED_TELEINFO_KEYS,
    UNUSED_CHARS_IN_TELEINFO,
    Teleinfo,
    TeleinfoLabel,
)


def decode_byte(byte_data: bytes) -> Result[str, str]:
    try:
        return Ok(byte_data.decode("utf-8"))
    except UnicodeDecodeError:
        return Err("invalid UTF-8.")
    except AttributeError:
        return Err("must be of type 'bytes'.")


def clean_data(data: str) -> Result[str, str]:
    try:
        return Ok(data.translate(str.maketrans(UNUSED_CHARS_IN_TELEINFO)))
    except (TypeError, AttributeError):
        return Err("must be of type 'string'")


def split_data(cleaned_data: str) -> Result[list[str, str, str], str]:
    if (
        not isinstance(cleaned_data, str)
        or len(cleaned_data) < 5
        or " " not in cleaned_data
    ):
        return Err(f"Can't split : {cleaned_data}")

    splitted = cleaned_data.split()

    # On attend len = 3 (key,value,checksum) mais parfois le checksum
    # est un espace donc split le supprime
    if len(splitted) not in (2, 3):
        return Err(f"Can't split : {cleaned_data}")

    # Si splitted a une longueur de 2 ou 3
    # key = splitted[1]
    # value = splitted[2]
    # checksum = dernier caractère de cleaned_data
    return Ok([*splitted[:2], cleaned_data[-1]])


def calculate_checksum(key: str, value: str) -> Result[str, str]:
    """
    La "checksum" est calculée sur l'ensemble des caractères allant du début
    du champ étiquette à la fin du champ donnée, caractère SP inclus.
    On fait tout d'abord la somme des codes ASCII de tous ces caractères.
    Pour éviter d'introduire des fonctions ASCII (00 à 1F en hexadécimal),
    on ne conserve que les six bits de poids faible du résultat obtenu
    (cette opération se traduit par un ET logique entre la somme précédemment
    calculée et 03Fh). Enfin, on ajoute 20 en hexadécimal.
    Le résultat sera donc toujours un caractère ASCII imprimable
    (signe, chiffre, lettre majuscule) allant de 20 à 5F en Hexadécimal.

    !!! 20 est le caractère espace !!!
    """
    if not all(isinstance(var, str) for var in (key, value)):
        return Err("'key' and 'value' must be of type 'str'.")

    data = key + " " + value
    # Calculer la somme des codes ASCII des caractères de key et value
    ascii_sum = sum(ord(c) for c in data)
    # Conserver les 6 bits de poids faible
    low_6_bits = ascii_sum & 0x3F
    # Ajouter 20 en hexadécimal
    checksum = low_6_bits + 0x20
    return Ok(chr(checksum))


def data_is_valid(key: str, value: str, checksum: str) -> Result[bool, str]:
    if not all(isinstance(var, str) for var in (key, value, checksum)):
        return Err("params must be of type 'str'.")
    match calculate_checksum(key, value):
        case Ok(calculated_checksum):
            if calculated_checksum == checksum:
                return Ok(True)
            else:
                return Err("calculated_checksum != checksum")
        case Err(e):
            return Err(e)


def get_data_in_line(byte_data: bytes) -> Result[tuple[str, str], str]:
    match decode_byte(byte_data):
        case Ok(data):
            pass
        case Err(e):
            return Err(e)

    match clean_data(data):
        case Ok(cleaned_data):
            pass
        case Err(e):
            return Err(e)

    match split_data(cleaned_data):
        case Ok(splitted_data):
            key, value, checksum = splitted_data
        case Err(e):
            return Err(e)

    match data_is_valid(key, value, checksum):
        case Ok(_):
            return Ok((key, value))
        case Err(e):
            return Err(e)


def buffer_can_accept_new_data(key: str, buffer: dict[str, str]) -> Result[bool, str]:
    if not isinstance(buffer, dict):
        return Err("'buffer' must be of type 'dict'.")
    if not isinstance(key, str):
        return Err("'key' must be of type 'str'.")

    return Ok(
        # on ne peut commencer à écrire dans le buffer qu'en début de trame donc si
        # le buffer est vide et que la clé est la première attendue dans la trame
        (not buffer and key == FIRST_TELEINFO_FRAME_KEY)
        # ou la première clé attendue dans la trame est déjà présente dans le buffer
        or FIRST_TELEINFO_FRAME_KEY in buffer.keys()
    )


def teleinfo_frame_is_complete(buffer: dict[str, str]) -> Result[bool, str]:
    if not isinstance(buffer, dict):
        return Err("'buffer' must be of type 'dict'.")
    return Ok(all(key in buffer for key in REQUIRED_TELEINFO_KEYS))


def get_available_intensity(teleinfo: Teleinfo) -> Result[int, str]:
    try:
        return Ok(
            int(teleinfo.data[TeleinfoLabel.ISOUSC])
            - int(teleinfo.data[TeleinfoLabel.IINST])
        )
    except KeyError:
        return Err(
            f"Missing {TeleinfoLabel.ISOUSC} or {TeleinfoLabel.IINST} in teleinfo data"
        )
    except ValueError:
        return Err(f"Invalid value for {TeleinfoLabel.ISOUSC} or {TeleinfoLabel.IINST}")
