import pytest
from result import Ok, Err
from teleinfo.constants import (
    FIRST_TELEINFO_FRAME_KEY,
    UNUSED_CHARS_IN_TELEINFO,
    Teleinfo,
    TeleinfoLabel,
)
from teleinfo.services import (
    buffer_can_accept_new_data,
    calculate_checksum,
    clean_data,
    data_is_valid,
    decode_byte,
    get_available_intensity,
    get_data_in_line,
    split_data,
    teleinfo_frame_is_complete,
)


@pytest.mark.parametrize(
    "byte_data, expected_result",
    [
        (b"Hello", Ok("Hello")),
        (b"\xff\xfe", Err("invalid UTF-8.")),
        ("Hello", Err("must be of type 'bytes'.")),
    ],
)
def test_decode_byte(byte_data, expected_result):
    assert decode_byte(byte_data) == expected_result


@pytest.mark.parametrize(
    "data, expected_result",
    [(f"{char}example{char}", Ok("example")) for char in UNUSED_CHARS_IN_TELEINFO]
    + [
        ("example", Ok("example")),
        ("\r\nexample\x02\x03", Ok("example")),
        (123, Err("must be of type 'string'")),
    ],
)
def test_clean_data(data, expected_result):
    assert clean_data(data) == expected_result


@pytest.mark.parametrize(
    "cleaned_data, expected",
    [
        (b"key value c", Err("Can't split : b'key value c'")),
        (12345, Err("Can't split : 12345")),
        ("k v ", Err("Can't split : k v ")),
        ("keyvalue", Err("Can't split : keyvalue")),
        ("keykeykey ", Err("Can't split : keykeykey ")),
        ("key value c extra", Err("Can't split : key value c extra")),
        ("key value c", Ok(["key", "value", "c"])),
        ("key value ", Ok(["key", "value", " "])),
        ("", Err("Can't split : ")),
    ],
)
def test_split_data(cleaned_data, expected):
    assert split_data(cleaned_data) == expected


@pytest.mark.parametrize(
    "key, value, expected",
    [
        ("KEY", "VALUE", Ok("&")),
        ("A", "A", Ok("B")),
        ("ZZZZ", "ZZZZ", Ok("P")),
        (123, "VALUE", Err("'key' and 'value' must be of type 'str'.")),
        ("KEY", None, Err("'key' and 'value' must be of type 'str'.")),
    ],
)
def test_calculate_checksum(key, value, expected):
    assert calculate_checksum(key, value) == expected


@pytest.mark.parametrize(
    "key, value, checksum, expected",
    [
        ("KEY", "VALUE", "&", Ok(True)),
        ("KEY", "VALUE", "A", Err("calculated_checksum != checksum")),
        ("KEY", 123, "&", Err("params must be of type 'str'.")),
    ],
)
def test_data_is_valid(key, value, checksum, expected):
    assert data_is_valid(key, value, checksum) == expected


import pytest


@pytest.mark.parametrize(
    "byte_data, expected",
    [
        (b"KEY VALUE &\n", Ok(("KEY", "VALUE"))),
        (b"\xff\xfe", Err("invalid UTF-8.")),
        (b"k v ", Err("Can't split : k v ")),
        (b"KEY VALUE A", Err("calculated_checksum != checksum")),
    ],
)
def test_get_data_in_line(byte_data, expected):
    assert get_data_in_line(byte_data) == expected


@pytest.mark.parametrize(
    "key, buffer, expected",
    [
        (FIRST_TELEINFO_FRAME_KEY, [], Err("'buffer' must be of type 'dict'.")),
        (1234, {}, Err("'key' must be of type 'str'.")),
        (FIRST_TELEINFO_FRAME_KEY, {}, Ok(True)),
        (TeleinfoLabel.HCHC, {FIRST_TELEINFO_FRAME_KEY: "value"}, Ok(True)),
        (FIRST_TELEINFO_FRAME_KEY, {TeleinfoLabel.HCHC: "value"}, Ok(False)),
        (TeleinfoLabel.ISOUSC, {TeleinfoLabel.OPTARIF: "value"}, Ok(False)),
    ],
)
def test_buffer_can_accept_new_data(key, buffer, expected):
    assert buffer_can_accept_new_data(key, buffer) == expected


import pytest

# Clés requises pour le test
REQUIRED_TELEINFO_KEYS = [
    "ADCO",
    "MOTDETAT",
    "IINST",
    "ISOUSC",
]


@pytest.mark.parametrize(
    "buffer, expected",
    [
        ([], Err("'buffer' must be of type 'dict'.")),
        ({key: "value" for key in REQUIRED_TELEINFO_KEYS}, Ok(True)),
        ({key: "value" for key in REQUIRED_TELEINFO_KEYS[1:]}, Ok(False)),
    ],
)
def test_teleinfo_frame_is_complete(buffer, expected):
    assert teleinfo_frame_is_complete(buffer) == expected


@pytest.mark.parametrize(
    "teleinfo_data, expected",
    [
        ({TeleinfoLabel.ISOUSC: "30", TeleinfoLabel.IINST: "10"}, Ok(20)),
        (
            {
                TeleinfoLabel.ISOUSC: "30",
                TeleinfoLabel.IINST: "10",
                TeleinfoLabel.OPTARIF: "HC..",
            },
            Ok(20),
        ),
        (
            {TeleinfoLabel.OPTARIF: "30", TeleinfoLabel.IINST: "10"},
            Err(
                f"Missing {TeleinfoLabel.ISOUSC} or {TeleinfoLabel.IINST} in teleinfo data"
            ),
        ),
        (
            {TeleinfoLabel.ISOUSC: "ABC", TeleinfoLabel.IINST: "10"},
            Err(f"Invalid value for {TeleinfoLabel.ISOUSC} or {TeleinfoLabel.IINST}"),
        ),
    ],
)
def test_get_available_intensity(teleinfo_data, expected):
    teleinfo = Teleinfo(data=teleinfo_data)
    assert get_available_intensity(teleinfo) == expected
