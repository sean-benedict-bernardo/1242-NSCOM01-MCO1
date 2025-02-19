import os


def fileExists(filename: str) -> bool:
    """Checks if a file exists"""
    return os.path.exists(f"client/{filename}")


def makeFolder() -> None:
    """Creates a directory if it does not exist"""
    if not os.path.exists("client"):
        print("Creating client folder...\n")
        try:
            os.makedirs("client")
        except:
            pass


def writeFile(filename: str, content: bytes) -> None:
    """Writes content to a file"""

    file = open(f"client/{filename}", "wb")
    file.write(content)
    file.close()


def readFile(filename: str, numBytes: int = -1) -> bytes | list[dict[str, bytes]]:
    """
    Reads a file and returns its content as bytes
    If a numBytes is provided, a bytearray of that size for each chunk is returned
    """
    try:
        file = open(f"client/{filename}", "rb")

        # check if file is empty
        if os.stat(f"client/{filename}").st_size == 0:
            return {1: b""}

        blockNumber = 1

        fileContent = b"" if numBytes == -1 else {}

        if numBytes != -1:
            while True:
                chunk = file.read(numBytes)
                if not chunk:
                    break
                fileContent[blockNumber] = chunk
                blockNumber += 1
        else:
            fileContent = file.read()

        file.close()

        return fileContent

    except FileNotFoundError as e:
        raise e
    except Exception as e:
        print(f"Error reading file: {e}")
