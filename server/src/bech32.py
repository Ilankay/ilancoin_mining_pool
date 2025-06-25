from exceptions import InvalidAddr

def bech32_decode(address):
    try:
        characters = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
        separator_position = address.rindex("1")
        hrp = address[:separator_position]
        data = address[separator_position + 1:]

        data_5_bits = [characters.index(c) for c in data]

        version_5_bits = data_5_bits.pop(0)
        checksum_5_bits = data_5_bits[-6:]
        witness_program_5_bits = data_5_bits[:-6]
        hrp_values = [ord(c) for c in hrp]

        hrp_expanded = [(v >> 5) for v in hrp_values] + [0] + [(v & 0b11111) for v in hrp_values]
        combined = hrp_expanded + [version_5_bits] + witness_program_5_bits
        combined_with_padding = combined + [0] * 6

        generator = [
            0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3
        ]

        checksum = 1
        for v in combined_with_padding:
            top = checksum >> 25
            checksum = (checksum & 0x1ffffff) << 5 ^ v
            for i in range(5):
                if (top >> i) & 1:
                    checksum ^= generator[i]

        constant = 1 if version_5_bits == 0 else 0x2bc830a3
        checksum ^= constant

        checksum_verify = [(checksum >> (5 * (5 - i))) & 0b11111 for i in range(6)]

        if checksum_5_bits != checksum_verify:raise InvalidAddr

        from_bits, to_bits = 5, 8
        accumulator, counter = 0, 0
        max_value = (1 << to_bits) - 1
        max_accumulator = (1 << (from_bits + to_bits - 1)) - 1
        witness_program_8_bits = []

        for int_5_bits in witness_program_5_bits:
            if int_5_bits < 0 or (int_5_bits >> from_bits) != 0:
                break
            accumulator = ((accumulator << from_bits) | int_5_bits) & max_accumulator
            counter += from_bits
            while counter >= to_bits:
                counter -= to_bits
                witness_program_8_bits.append((accumulator >> counter) & max_value)


        witness_program_hex = ''.join(f"{v:02x}" for v in witness_program_8_bits)
    except Exception:
        raise InvalidAddr

    return witness_program_hex

