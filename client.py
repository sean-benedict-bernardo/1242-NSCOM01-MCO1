"""
TFTPv2 Client Implementation
as defined by RFC 1350

NSCOM01 S13
Strebel, Adler Clarence E.
Bernardo, Sean Benedict G.
"""

# Custom imports
import files
import misc

# Python imports
import socket


IP, PORT = "127.0.0.1", 69
CLIENTPORT = 51125  # u-i-i-a-u in lol

# TODO: attach this to client class to allow for negotiation as per RFCs 2347, 2348, and 2349
DATALENGTH = 512


class Client:
    def __init__(self):
        self.destIP = self.setDestination()
        self.destReqPort = 69  # nice
        self.clientPort = CLIENTPORT

        self.setSocket()
        self.loop()

    def __del__(self):
        # Ensure that the socket is closed when the client is deleted
        if hasattr(self, "sock"):
            self.sock.close()

    def loop(self):
        """Main loop for the client"""
        while True:
            userInput = int(
                misc.getInput(
                    "What would you like to do ",
                    ["Download File", "Upload", "Change Server IP", "Exit"],
                )
            )

            match userInput:
                case 0:
                    # Download File
                    try:
                        filename = misc.getInput("Enter filename to retrieve: ")
                        self.sendRequest("RRQ", filename)
                        fileData = self.receiveFile()

                        if fileData:
                            files.writeFile(filename, fileData)
                    except Exception as e:
                        # file cannot be retrieved
                        print(e)
                        pass
                case 1:
                    # Send File
                    try:
                        filename = misc.getInput("Enter filename to upload: ")

                        fileData = files.readFile(filename, DATALENGTH)

                        if fileData:
                            self.sendRequest("WRQ", filename)
                            self.sendFile(fileData)
                    except FileNotFoundError:
                        print(f'File "{filename}" not found')
                    except:
                        pass
                case 2:
                    self.destIP = self.setDestination()
                    self.setSocket()
                case 3:
                    print("\nExiting...\n")
                    return

    def setDestination(self):
        """Set destination IPv4 address with checks for valid IP address"""
        # TODO: add support for IPv6

        while True:
            localIP = misc.getInput("Enter destination IP address: ")
            # Check if IP is valid
            if localIP == "localhost":
                return localIP
            octets = localIP.split(".")
            if len(localIP.split(".")) != 4:
                print("Invalid IP")
                continue
            for octet in octets:
                if not octet.isdigit() or int(octet) < 0 or int(octet) > 255:
                    print("Invalid IP")
                    continue
            return localIP

    def setSocket(self):
        """Bind socket to IP and port"""

        # unbind if already bound
        if hasattr(self, "sock"):
            self.sock.close()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.sock.bind(("", self.clientPort))

    def sendRequest(self, mode, filename):
        """Sends a request to the server"""

        if mode not in ["RRQ", "WRQ"]:
            # if this is somehow thrown, im an idiot
            raise ValueError("Invalid mode, author is an idiot")

        # See RFC 1350, sec. 5, figure 5-1
        packet = (
            b"\x00"
            + (b"\x01" if mode == "RRQ" else b"\x02")
            + filename.encode("utf-8")
            + b"\x00octet\x00"
        )
        self.sock.sendto(packet, (self.destIP, self.destReqPort))

    def parseData(self, rawdata: bytes):
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
                errorcode, errmessage = int.from_bytes(rawdata[2:4]), rawdata[4:-2]
                return {
                    "opcode": opcode,
                    "errorcode": errorcode,
                    "errmessage": errmessage,
                }

        return {"opcode": opcode}

    def receiveFile(self):
        """Listens for UDP packets containing file data"""

        def sendAck(blockNumber: int, transferPort: int):
            """Sends an acknowledgment to the server"""
            packet = b"\x00\x04" + blockNumber.to_bytes(2)
            self.sock.sendto(packet, (self.destIP, transferPort))

        # have a list of the previous blocks
        # for duplicate detection and reordering
        uniquePackets = []

        # this variable becomes true when the last packet comes in
        # while there are potentially other packets still being sent
        checkOrder = False

        while True:
            try:
                # 5 second time-out
                self.sock.settimeout(1)
                # 4 = 2 Byte opcode + 2 byte block number for DATA
                data, server = self.sock.recvfrom(DATALENGTH + 4)
                transferPort = server[1]

                data = self.parseData(data)

                if data["opcode"] == 3:
                    blockNumbers = list(
                        sorted(map(lambda x: x["block"], uniquePackets))
                    )

                    # for every DATA packet received, check if packet with that block number is received
                    # we discard the packet if it is already recieved,
                    # append it to the unique packet otherwise
                    if data["block"] not in blockNumbers:
                        # There are occasions that a packet with 0 bytes of data will be added
                        # This is fine 🔥🔥🔥
                        uniquePackets.append(data)
                        sendAck(data["block"], transferPort)

                        # See RFC 1350, sec. 6 for termination process
                        # The extra stuff here is to acccount for out of sequence packet arrival
                        if len(data["data"]) != DATALENGTH or checkOrder:
                            # check if list of block numbers is complete
                            checkOrder = blockNumbers == list(
                                range(1, data["block"] + 1)
                            )
                            if not checkOrder:
                                break
                    else:
                        # Tell user that duplicate data is found
                        print(f"Duplicate DATA found; Block Num: {data["block"]}")
                elif data["opcode"] == 5:
                    print(
                        f"ERROR [0x0{data["errorcode"]}]: {data["errmessage"].decode('utf-8')}"
                    )

            except TimeoutError:
                if data and data["opcode"] == 3:
                    sendAck(data["block"], transferPort)
                else:
                    break
                pass
            except ConnectionResetError:
                print("Server connection lost")
                break
            except Exception as err:
                print(type(err).__name__, err)
                break

        if len(uniquePackets) == 0:
            raise Exception("File cannot be retrieved")

        # Sort data by block sequence number
        uniquePackets.sort(key=lambda data: data["block"])

        # join blocks together
        fileData = b"".join(list(map(lambda packet: packet["data"], uniquePackets)))

        return fileData

    def sendFile(self, filecontent: list[dict[int, bytes]]) -> None:
        """Splits file content into packets and sends them to the server"""

        sentBlocks = []

        def sendBlock(blockNumber: int, data: bytes, transferPort: int) -> None:
            """Sends a block to the server"""
            try:
                packet = b"\x00\x03" + blockNumber.to_bytes(2) + data
                self.sock.sendto(packet, (self.destIP, transferPort))
            except Exception as e:
                print(e)

        while True:
            try:
                # 5 second time-out
                self.sock.settimeout(5)

                # listen for ACKs and ERRORs
                data, server = self.sock.recvfrom(DATALENGTH + 4)
                transferPort = server[1]

                if data:
                    data = self.parseData(data)
                else:
                    continue

                # Skip duplicate ACKs
                if data["block"] in sentBlocks:
                    print(f"Duplicate ACK found; Block Num: {data["block"]}")
                    continue

                match data["opcode"]:
                    case 4:
                        # print(f"ACK: Block {data["block"]}") # DEBUG ONLY
                        sentBlocks.append(data["block"])

                        nextBlock = data["block"] + 1

                        if nextBlock in filecontent:
                            sendBlock(nextBlock, filecontent[nextBlock], transferPort)
                        else:
                            print("File sent successfully!")
                            return
                    case 5:
                        print(
                            f"ERROR [0x0{data["errorcode"]}]: {data["errmessage"].decode('utf-8')}"
                        )

            except ConnectionResetError:
                # idk why or how this exception is even possible in UDP but it is
                print("Server connection lost")
                break

            except TimeoutError:
                if data and data["opcode"] == 4:
                    print(f"TIMEOUT: Resending block {data["block"] + 1}")
                    sendBlock(filecontent[data["block"] + 1], transferPort)
                else:
                    break
            except Exception as e:
                break


if __name__ == "__main__":
    misc.onStart()

    client = Client()
