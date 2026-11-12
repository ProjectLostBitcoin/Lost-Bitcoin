"""
Lost Bitcoin — Bitcoin address validation (pure standard library).

Validates the *format* of a Bitcoin address only:
  - Legacy Base58Check (P2PKH / P2SH, mainnet + testnet)
  - SegWit Bech32 (v0) and Bech32m (v1+, e.g. Taproot), BIP-173 / BIP-350

A valid format does NOT prove ownership, balance, or recoverability.
It only proves the string is a well-formed address (correct charset,
length and checksum), so typos are caught before an address is saved
to an investigation or sent to a blockchain API.
"""

import hashlib

_B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_B58_INDEX = {c: i for i, c in enumerate(_B58_ALPHABET)}

_BECH32_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
_BECH32_INDEX = {c: i for i, c in enumerate(_BECH32_CHARSET)}
_BECH32_CONST = 1
_BECH32M_CONST = 0x2BC830A3


def _base58_decode(text):
    num = 0
    for ch in text:
        if ch not in _B58_INDEX:
            raise ValueError("Invalid Base58 character.")
        num = num * 58 + _B58_INDEX[ch]
    raw = num.to_bytes((num.bit_length() + 7) // 8, "big") if num else b""
    pad = len(text) - len(text.lstrip("1"))
    return b"\x00" * pad + raw


def _validate_base58check(address):
    raw = _base58_decode(address)
    if len(raw) != 25:
        raise ValueError("Invalid address length.")
    payload, checksum = raw[:-4], raw[-4:]
    digest = hashlib.sha256(hashlib.sha256(payload).digest()).digest()
    if digest[:4] != checksum:
        raise ValueError("Invalid address checksum.")
    version = payload[0]
    kinds = {
        0x00: ("p2pkh", "mainnet"),
        0x05: ("p2sh", "mainnet"),
        0x6F: ("p2pkh", "testnet"),
        0xC4: ("p2sh", "testnet"),
    }
    if version not in kinds:
        raise ValueError("Unknown address version.")
    kind, network = kinds[version]
    return {"valid": True, "type": kind, "network": network, "encoding": "base58check"}


def _bech32_polymod(values):
    chk = 1
    generators = (0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3)
    for value in values:
        top = chk >> 25
        chk = ((chk & 0x1FFFFFF) << 5) ^ value
        for i in range(5):
            if (top >> i) & 1:
                chk ^= generators[i]
    return chk


def _bech32_hrp_expand(hrp):
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]


def _convertbits(data, from_bits, to_bits, pad=True):
    acc, bits, out = 0, 0, []
    maxv = (1 << to_bits) - 1
    for value in data:
        acc = (acc << from_bits) | value
        bits += from_bits
        while bits >= to_bits:
            bits -= to_bits
            out.append((acc >> bits) & maxv)
    if pad:
        if bits:
            out.append((acc << (to_bits - bits)) & maxv)
    elif bits >= from_bits or ((acc << (to_bits - bits)) & maxv):
        return None
    return out


def _validate_segwit(address):
    lowered = address.lower()
    if lowered != address and address.upper() != address:
        raise ValueError("Mixed-case Bech32 addresses are invalid.")
    address = lowered
    pos = address.rfind("1")
    if pos < 1:
        raise ValueError("Invalid Bech32 separator.")
    hrp, data_part = address[:pos], address[pos + 1:]
    if hrp not in ("bc", "tb"):
        raise ValueError("Unknown Bech32 human-readable part.")
    if len(data_part) < 6 or any(c not in _BECH32_INDEX for c in data_part):
        raise ValueError("Invalid Bech32 data.")
    data = [_BECH32_INDEX[c] for c in data_part]
    polymod = _bech32_polymod(_bech32_hrp_expand(hrp) + data)
    version = data[0]
    if version > 16:
        raise ValueError("Invalid witness version.")
    expected = _BECH32_CONST if version == 0 else _BECH32M_CONST
    if polymod != expected:
        raise ValueError("Invalid Bech32 checksum.")
    program = _convertbits(data[1:-6], 5, 8, pad=False)
    if program is None or not (2 <= len(program) <= 40):
        raise ValueError("Invalid witness program length.")
    if version == 0 and len(program) not in (20, 32):
        raise ValueError("Invalid v0 witness program length.")
    if version == 1 and len(program) != 32:
        raise ValueError("Invalid v1 witness program length.")
    kind = {0: "segwit_v0", 1: "taproot"}.get(version, f"segwit_v{version}")
    return {
        "valid": True,
        "type": kind,
        "network": "mainnet" if hrp == "bc" else "testnet",
        "encoding": "bech32" if version == 0 else "bech32m",
    }


def validate_bitcoin_address(address):
    """
    Return {'valid': True, 'type': ..., 'network': ..., 'encoding': ...}
    or raise ValueError with a plain-English reason.
    """
    if not isinstance(address, str):
        raise ValueError("Bitcoin address must be text.")
    address = address.strip()
    if not address:
        raise ValueError("Bitcoin address cannot be empty.")
    if any(c.isspace() for c in address):
        raise ValueError("Bitcoin address cannot contain spaces.")
    lowered = address.lower()
    if lowered.startswith(("bc1", "tb1")):
        return _validate_segwit(address)
    if address[0] in "13mn2":
        return _validate_base58check(address)
    raise ValueError("This does not look like a Bitcoin address.")
