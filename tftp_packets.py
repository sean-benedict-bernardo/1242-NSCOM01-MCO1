import misc

OPCODES = {1: "RRQ", 2: "WRQ", 3: "DATA", 4: "ACK", 5: "ERROR"}

ERRORCODES = {
    0: "Not defined, see error message (if any).",
    1: "File not found.",
    2: "Access violation.",
    3: "Disk full or allocation exceeded.",
    4: "Illegal TFTP operation.",
    5: "Unknown transfer ID.",
    6: "File already exists.",
    7: "No such user.",
}


def printError(packet) -> None:
    """Prints error message based on error code"""
    errcode = packet["errorcode"]
    errmessage = packet["errmessage"]

    if errcode in ERRORCODES and errcode != 0:
        print(f"ERROR [0x{"{:02d}".format(errcode)}]: {ERRORCODES[errcode]}")
    else:
        print(f"ERROR [0x{"{:02d}".format(errcode)}]: {errmessage}")

    print()


def appendOptions(mode: str) -> dict:
    options = {}

    while True and len(options.keys()) < 2:
        tempOption = misc.getInput(
            "What options would you like to append",
            ["Block size", "Transfer Communication size", "None"],
        )

        match tempOption:
            case 0:
                while True:
                    try:
                        blocksize = misc.getInput("Enter block size: ")
                        # Check if block size is a number and within the valid range as per RFC 2348
                        if (
                            blocksize.isdigit()
                            and 8 <= int(blocksize)
                            and int(blocksize) <= 65464
                        ):
                            options["blksize"] = int(blocksize)
                            break
                        elif blocksize.isdigit():
                            print("Block size must be between 8 and 65464")
                    except KeyboardInterrupt:
                        break
            case 1:
                while True:
                    try:
                        # In Read Request packets, a size of "0" is specified in the request
                        # and the size of the file, in octets, is returned in the OACK.
                        if mode == "RRQ":
                            options["tsize"] = 0
                            break
                        else:
                            tsize = misc.getInput("Enter transfer size: ")
                            if tsize.isdigit():
                                options["tsize"] = int(tsize)
                                break
                    except KeyboardInterrupt:
                        break
            case 2:
                break

    return options


def parseData(rawdata: bytes):
    """Parses data packet by extracting opcode and relevant data depending on opcode"""
    # got this trick from geeks for geeks
    # https://www.geeksforgeeks.org/how-to-convert-bytes-to-int-in-python/
    opcode = int.from_bytes(rawdata[:2])

    match opcode:
        # DATA
        case 3:
            block, data = int.from_bytes(rawdata[2:4]), rawdata[4:]
            return {"opcode": opcode, "block": block, "data": data}
        # ACK
        case 4:
            block = int.from_bytes(rawdata[2:4])
            return {"opcode": opcode, "block": block}
        # ERROR
        case 5:
            errorcode, errmessage = int.from_bytes(rawdata[2:4]), rawdata[4:-2].decode(
                "utf-8"
            )

            return {
                "opcode": opcode,
                "errorcode": errorcode,
                "errmessage": errmessage,
            }
        # OACK
        case 6:
            data = rawdata[2:]

            # split data by null byte, omit last element as its empty
            data = data.split(b"\x00")[0:-1]

            options = {}

            for i in range(0, len(data), 2):
                optionType, optionData = data[i].decode("utf-8"), data[i + 1].decode(
                    "utf-8"
                )

                if optionType in ["blksize", "tsize"]:
                    optionData = int(optionData)

                options[optionType] = optionData

            return {"opcode": opcode, "options": options}

    return {"opcode": opcode}
