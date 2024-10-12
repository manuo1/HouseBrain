# teleinfo lines sample:
# b'ADCO 021728123456 =\r\n'
# b'OPTARIF HC.. <\r\n'
# b'ISOUSC 45 ?\r\n'
# b'HCHC 050977332 *\r\n'
# b'HCHP 056567645 ?\r\n'
# b'PTEC HP..  \r\n'
# b'IINST 004 [\r\n'
# b'IMAX 057 K\r\n'
# b'PAPP 00850 .\r\n'
# b'HHPHC E 0\r\n'
# b'MOTDETAT 000000 B\r\x03\x02\n'


from teleinfo.constants import (
    FIRST_TELEINFO_FRAME_KEY,
    INVALIDE_KEY,
    LAST_TELEINFO_FRAME_KEY,
)


def decode_byte(byte_data):
    try:
        return byte_data.decode("utf-8")
    except UnicodeDecodeError:
        return ""


def clean_data(data):
    remove_chars = {
        "\r": "",  # Carriage Return
        "\n": "",  # New line
        "\x03": "",  # End of Text (ETX)
        "\x02": "",  # Start of Text (STX)
    }
    # Utilisation de str.translate pour appliquer toutes les remplacements en une fois
    return data.translate(str.maketrans(remove_chars))


def split_data(cleaned_data):
    default_splitted = [" ", " ", " "]
    if not cleaned_data:
        return default_splitted

    splitted = cleaned_data.split(" ")

    # sometimes the checksum (last character) is a space which breaks the split logic
    if cleaned_data[-1] == " " and len(splitted) >= 3:
        splitted = [*splitted[:2], " "]

    # must have 3 elements in list (key, value, checksum)
    if len(splitted) != 3:
        return default_splitted

    return splitted


def calculate_checksum(key, value):
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
    """
    data = key + " " + value
    # Calculer la somme des codes ASCII des caractères de l'étiquette et de la valeur
    ascii_sum = sum(ord(c) for c in data)
    # Conserver les 6 bits de poids faible
    low_6_bits = ascii_sum & 0x3F
    # Ajouter 20 en hexadécimal
    checksum = low_6_bits + 0x20
    return chr(checksum)


def data_is_valid(key, value, checksum):
    return checksum == calculate_checksum(key, value)


def get_data_in_line(byte_data):
    data = decode_byte(byte_data)
    cleaned_data = clean_data(data)
    key, value, checksum = split_data(cleaned_data)
    if data_is_valid(key, value, checksum):
        return key, value
    return INVALIDE_KEY, INVALIDE_KEY


def teleinfo_frame_is_complete(buffer):
    return all(
        key in buffer for key in [FIRST_TELEINFO_FRAME_KEY, LAST_TELEINFO_FRAME_KEY]
    )


def add_data_to_buffer(key: str, value: str, buffer: dict) -> dict:
    if not key == INVALIDE_KEY and key not in buffer.keys():
        buffer[key] = value

    # si LAST_TELEINFO_FRAME_KEY et present sans LAST_TELEINFO_FRAME_KEY
    # cela veux dire que l'on a commencé à enregistrer la trame au milieu
    # donc on ne garde pas cette trame
    if key == LAST_TELEINFO_FRAME_KEY and FIRST_TELEINFO_FRAME_KEY not in buffer.keys():
        buffer.clear()

    return buffer
