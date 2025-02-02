OPCODES = {1: "RRQ", 2: "WRQ", 3: "DATA", 4: "ACK", 5: "ERROR"}

ERRORCODES = {
    # 0: "Not defined, see error message (if any).", 
    1: "File not found.",
    2: "Access violation.",
    3: "Disk full or allocation exceeded.",
    4: "Illegal TFTP operation.",
    5: "Unknown transfer ID.",
    6: "File already exists.",
    7: "No such user.",
}


def parsePacket(packet: bytes) -> tuple:
    """Parses a packet and returns its opcode and data"""
    opcode = int.from_bytes(packet[:2], "big")
    data = packet[2:]
    return (opcode, data)