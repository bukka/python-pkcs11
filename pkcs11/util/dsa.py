"""
Key handling utilities for DSA keys.

These utilities depend on :mod:`pyasn1` and :mod:`pyasn1_modules`.
"""

from pyasn1.codec.der import encoder, decoder
from pyasn1_modules.rfc3279 import Dss_Parms, Dss_Sig_Value, DSAPublicKey

from . import biginteger
from ..constants import Attribute


def decode_dsa_domain_parameters(der):
    """
    Decode RFC 3279 DER-encoded Dss-Params.

    :param bytes der: DER-encoded parameters
    :rtype: dict(Attribute,*)
    """

    params, _ = decoder.decode(der, asn1Spec=Dss_Parms())

    return {
        Attribute.BASE: biginteger(params['g']),
        Attribute.PRIME: biginteger(params['p']),
        Attribute.SUBPRIME: biginteger(params['q']),
    }


def encode_dsa_domain_parameters(obj):
    """
    Encode RFC 3279 DER-encoded Dss-Params.

    :param DomainParameters obj: domain parameters
    :rtype: bytes
    """
    asn1 = Dss_Parms()
    asn1['g'] = int.from_bytes(obj[Attribute.BASE], byteorder='big')
    asn1['p'] = int.from_bytes(obj[Attribute.PRIME], byteorder='big')
    asn1['q'] = int.from_bytes(obj[Attribute.SUBPRIME], byteorder='big')

    return encoder.encode(asn1)


def encode_dsa_public_key(key):
    """
    Encode DSA public key into RFC 3279 DER-encoded format.

    :param PublicKey key: public key
    :rtype: bytes
    """

    asn1 = DSAPublicKey(int.from_bytes(key[Attribute.VALUE], byteorder='big'))

    return encoder.encode(asn1)


def decode_dsa_public_key(der):
    """
    Decode a DSA public key from RFC 3279 DER-encoded format.

    Returns a `biginteger` encoded as bytes.

    :param bytes der: DER-encoded public key
    :rtype: bytes
    """

    asn1, _ = decoder.decode(der, asn1Spec=DSAPublicKey())
    return biginteger(asn1)


def encode_dsa_signature(signature):
    """
    Encode a signature (generated by :meth:`pkcs11.SignMixin.sign`) into
    DER-encoded ASN.1 (Dss_Sig_Value) format.

    :param bytes signature: signature as bytes
    :rtype: bytes
    """

    part = len(signature) // 2
    r, s = signature[:part], signature[part:]

    asn1 = Dss_Sig_Value()
    asn1['r'] = int.from_bytes(r, byteorder='big')
    asn1['s'] = int.from_bytes(s, byteorder='big')

    return encoder.encode(asn1)


def decode_dsa_signature(der):
    """
    Decode a DER-encoded ASN.1 (Dss_Sig_Value) signature (as generated by
    OpenSSL) into PKCS #11 format.

    :param bytes der: DER-encoded signature
    :rtype bytes:
    """

    asn1, _ = decoder.decode(der, asn1Spec=Dss_Sig_Value())

    r = int(asn1['r'])
    s = int(asn1['s'])

    # r and s are both 20 bytes
    return b''.join((
        r.to_bytes(20, byteorder='big'),
        s.to_bytes(20, byteorder='big'),
    ))
