#!/usr/bin/env python3
"""
Embed a URL into a block of text using zero-width characters (steganography).

Usage: run the script. It prints the stego text to stdout and demonstrates decoding.

Encoding scheme:
- Base64-encode the URL to get bytes.
- Convert bytes to a bit string.
- Map '0' -> U+200B (ZERO WIDTH SPACE), '1' -> U+200C (ZERO WIDTH NON-JOINER).
- Insert zero-width characters after whitespace locations in the text sequentially. If bits remain, append them at the end.

This keeps the visible text unchanged while hiding the URL invisibly.
"""

import base64
import re
import sys

# The target URL to embed
URL = "https://www.youtube.com/watch?v=uTJ-7oPkcg4"

# The Tongan text to embed into (kept verbatim)
TEXT = """KOE TALATUPUA KI HE FETUU KO TAPUKITEA
Tokua koe ongo pango; ko Taputa mei Hahake, ko Kitea mei Hihifo. Pea fanongo ai a Kitea oku iai ‘ae pango i Hahake, pea mole ai o alu ki Hahake ke kumi kiai.

Pea au atu ‘ae pango fefine ko Kitea, oku fai ‘ae huo ma‘ala ‘ae pango tangata ko Tapu. Pea nofo leva he toumi ma‘ala o ui atu: “Pango tangata, hau ki heni.” Pea tuku leva ‘ene huo kae alu atu oma feiloaki.

Pea na o ki he ‘api o Tapu ke fafanga ai ‘ae fefine, pea na nonofo ai o fai ‘hono ‘api. Nae faifai pea feitama a Kitea pea lea ange kia Tapu kena o mua ki Hihifo ke fa‘ele ai.

Nae fanaui ‘ene tamasi‘i koe tama tangata, pea na alea ai ke hingoa pe kiate kinaua ko Tapukitea. Pea lahi ‘ene tamasi‘i, pea kehe ange ‘ene pau‘u. Pea nae ikai ha taha momoi mau ha fiemalie i he ita ‘ae hou’eiki moe kakai i he pau‘u ‘ene tamasi‘i.

Pea na alea ai ke lelei mua ke tamate‘i ‘ene tama ke aluo tu‘u pe mei langi ‘ene sio hake ki he kui na matu‘aki fui ‘ene anga. Pea na fai: Pea alu a Tapukitea o tu‘u mei langi, o talu ai ‘eni ‘ene tu‘u i langi."""

# Use four zero-width characters to encode 2 bits per character to increase density and obfuscation
ZW_MAP = {
    '00': '\u200B',  # ZERO WIDTH SPACE
    '01': '\u200C',  # ZERO WIDTH NON-JOINER
    '10': '\u200D',  # ZERO WIDTH JOINER
    '11': '\uFEFF',  # ZERO WIDTH NO-BREAK SPACE (rare)
}
INV_ZW_MAP = {v: k for k, v in ZW_MAP.items()}

def url_to_bits(url: str) -> str:
    """Base64-encode URL and return a string of bits."""
    b64 = base64.b64encode(url.encode('utf-8'))
    bits = ''.join(f"{byte:08b}" for byte in b64)
    return bits

def bits_to_zw_pairs(bits: str) -> str:
    """Convert bits into zero-width characters using 2-bit grouping."""
    # pad to multiple of 2
    if len(bits) % 2 != 0:
        bits += '0'
    out = []
    for i in range(0, len(bits), 2):
        pair = bits[i:i+2]
        out.append(ZW_MAP[pair])
    return ''.join(out)

def zw_pairs_to_bits(zw: str) -> str:
    """Convert zero-width characters back into a bit string using inverse mapping."""
    bits = []
    for ch in zw:
        if ch in INV_ZW_MAP:
            bits.append(INV_ZW_MAP[ch])
    return ''.join(bits)

def ensure_dir(path: str):
    import os
    dirp = os.path.dirname(path)
    if dirp and not os.path.exists(dirp):
        os.makedirs(dirp, exist_ok=True)

def embed_in_text_with_seed(plain: str, payload_zw: str, seed: int = None) -> tuple:
    """Embed zero-width payload into plain text using a seed-based permutation.

    - Reserve the first K whitespace positions to store the 16-bit seed (as 8 zero-width chars using 2-bit mapping).
    - Use the seed to permute the remaining whitespace positions and place payload characters there.
    - If not enough whitespace positions, append remaining payload at the end.
    Returns (stego_text, seed_used).
    """
    if not payload_zw:
        return plain, seed

    # find whitespace insertion points (positions after whitespace)
    inserts = [m.end() for m in re.finditer(r"\s", plain)]
    K = 8  # number of positions reserved for seed (8 zw chars => 16 bits)

    # choose seed if not provided
    if seed is None:
        seed = base64.b16encode(base64.b16encode(b'').lower()) if False else int.from_bytes(base64.b64encode(b'')[:2], 'big')
        # fallback: use time-based seed
        seed = int.from_bytes(base64.b64encode(b'')[:2], 'big') if seed == 0 else seed
        # simpler: use current time lower 16 bits
        import time
        seed = int(time.time()) & 0xFFFF

    # prepare seed as zw chars
    seed_bits = f"{seed:016b}"  # 16 bits
    seed_zw = ''.join(ZW_MAP[seed_bits[i:i+2]] for i in range(0, 16, 2))

    # Build an insertion map keyed by original string index (position after whitespace)
    insert_map = {}
    # seed in first K positions
    for i in range(min(K, len(inserts))):
        insert_map[inserts[i]] = seed_zw[i]

    remaining_points = inserts[K:]
    # create permutation of remaining indices using seeded PRNG
    import random
    rng = random.Random(seed)
    perm = list(range(len(remaining_points)))
    rng.shuffle(perm)

    tail_payload = ''
    for p in range(len(payload_zw)):
        if p < len(remaining_points):
            target_pos = remaining_points[perm[p]]
            insert_map[target_pos] = payload_zw[p]
        else:
            tail_payload += payload_zw[p]

    # Build output by slicing original string and inserting zw chars at mapped positions
    out_parts = []
    last = 0
    for pos in sorted(insert_map.keys()):
        out_parts.append(plain[last:pos])
        out_parts.append(insert_map[pos])
        last = pos
    out_parts.append(plain[last:])
    if tail_payload:
        out_parts.append(tail_payload)

    return ''.join(out_parts), seed

def extract_from_text_with_seed(stego: str) -> str:
    """Extract URL from stego text produced by embed_in_text_with_seed.

    Steps:
    - Find whitespace positions.
    - Read the first K zero-width characters after the first K whitespace positions to recover the seed.
    - Recreate permutation and read payload characters from the permuted positions.
    - Reconstruct bits and decode base64.
    """
    # find whitespace points
    inserts = [m.end() for m in re.finditer(r"\s", stego)]
    if not inserts:
        return ''
    K = 8
    # extract seed zw chars from first K positions
    seed_zw_chars = []
    for i in range(min(K, len(inserts))):
        idx = inserts[i]
        # check if a zw char exists immediately after this position
        if idx < len(stego) and stego[idx] in INV_ZW_MAP:
            seed_zw_chars.append(stego[idx])
        else:
            seed_zw_chars.append('\u0000')

    # convert seed_zw_chars to bits
    seed_bits = ''.join(INV_ZW_MAP.get(ch, '00') for ch in seed_zw_chars)
    try:
        seed = int(seed_bits, 2)
    except Exception:
        seed = 0

    # now get remaining whitespace positions and read their zero-width chars
    remaining_inserts = inserts[K:]
    # build permutation
    import random
    rng = random.Random(seed)
    perm = list(range(len(remaining_inserts)))
    rng.shuffle(perm)

    # collect payload zw chars according to permuted order
    payload_chars = []
    for j in perm:
        idx = remaining_inserts[j]
        ch = stego[idx] if idx < len(stego) else None
        if ch in INV_ZW_MAP:
            payload_chars.append(ch)

    # if nothing, try collecting all zw chars after K positions in text order
    # also collect any tail payload characters appended to the end
    all_zw = [ch for ch in stego if ch in INV_ZW_MAP]
    tail_len = len(all_zw) - K - len(payload_chars)
    if tail_len > 0:
        payload_chars.extend(all_zw[-tail_len:])

    bits = zw_pairs_to_bits(''.join(payload_chars))
    # trim to byte boundary
    n = (len(bits) // 8) * 8
    bits = bits[:n]
    b = bytearray()
    for i in range(0, len(bits), 8):
        byte = int(bits[i:i+8], 2)
        b.append(byte)
    try:
        decoded = base64.b64decode(bytes(b))
        return decoded.decode('utf-8')
    except Exception:
        return ''

def main():
    import argparse, os
    parser = argparse.ArgumentParser(description='Embed URL into Tongan text using zero-width stego')
    parser.add_argument('--out', '-o', help='Output path for stego text', default=os.path.join(os.path.dirname(__file__), 'secret', 'stego_hidden.txt'))
    args = parser.parse_args()

    bits = url_to_bits(URL)
    zw = bits_to_zw_pairs(bits)
    stego, seed_used = embed_in_text_with_seed(TEXT, zw)

    # ensure directory and write file
    out_path = args.out
    ensure_dir(out_path)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(stego)
    print(f'Stego text written to: {out_path}')

    # Demonstrate extraction/verification
    recovered = extract_from_text_with_seed(stego)
    print('\n--- Extracted URL (decoded) ---')
    print(recovered or '<none>')

if __name__ == '__main__':
    main()
