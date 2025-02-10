"""
TFTPv2 Client Implementation
as defined by RFC 1350

NSCOM01 S13
Strebel, Adler Clarence E.
Bernardo, Sean Benedict G.
"""

# Custom imports
import files, misc, packets

# Python imports
import socket, sys, time

IP, PORT = "127.0.0.1", 69
CLIENTPORT = 51125  # u-i-i-a-u in lol


class Client:
    def __init__(self, destIP: str = None):
        self.destIP = self.setDestination() if destIP == None else destIP
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
            print("============ TFTPv2 Client ============")
            print(f"Set Destination IP: {self.destIP}\n")
            userInput = int(
                misc.getInput(
                    f"What would you like to do",
                    ["Download File", "Upload", "Change Server IP", "Exit"],
                )
            )

            match userInput:
                case 0:
                    # Download File
                    try:
                        blksize = 512
                        filename = misc.getInput("Enter filename to retrieve: ")

                        options = packets.appendOptions("RRQ")

                        self.sendRequest("RRQ", filename, options)

                        # await OACK, skip if no options because
                        # regular TFTP will immediately send DATA
                        if len(options) > 0:
                            ackInit = self.awaitAck()

                            if ackInit["opcode"] == 5:
                                print("File cannot be retrieved")
                                continue

                            if ackInit["opcode"] == 6:
                                if "blksize" in ackInit["options"]:
                                    blksize = ackInit["options"]["blksize"]
                                    print(f"Block size set to {blksize}")
                                if "tsize" in ackInit["options"]:
                                    print(
                                        f"Incoming file size: {ackInit["options"]["tsize"]}"
                                    )

                                # Send ACK for OACK
                                self.sendAck(0, ackInit["transferPort"])

                        fileData = self.receiveFile(blksize)

                        if fileData:
                            files.writeFile(filename, fileData)
                            print(f"{filename} was retrieved successfully\n")
                        else: # File cannot be retrieved
                            print(f"{filename} cannot be retrieved\n")
                    except Exception:
                        # file cannot be retrieved
                        pass
                case 1:
                    # Send File
                    try:
                        blksize = 512
                        filename = misc.getInput("Enter filename to upload: ")

                        # Can specify filename to be used on server when uploading
                        filenameServer = misc.getInput(
                            "Enter filename to be used on server: "
                        )

                        # Defaults to filename on client if no server filename is specified
                        filenameServer = (
                            filenameServer
                            if filenameServer or filenameServer == ""
                            else filename
                        )

                        options = packets.appendOptions("WRQ")

                        if files.fileExists(filename):
                            self.sendRequest("WRQ", filenameServer, options)

                            ackInit = self.awaitAck()

                            # no additional behavior for opcode 4

                            if ackInit["opcode"] == 5:
                                print("File cannot be sent")
                                continue

                            if ackInit["opcode"] == 6:
                                if "blksize" in ackInit["options"]:
                                    blksize = ackInit["options"]["blksize"]
                                if "tsize" in ackInit["options"]:
                                    print(
                                        f"Number of bytes to be sent: {ackInit["options"]["tsize"]}"
                                    )

                            with files.readFile(filename, blksize) as fileContent:
                                self.sendFile(fileContent)

                    except FileNotFoundError:
                        print(f'File "{filename}" not found')
                    except:
                        pass
                case 2:
                    # unbind if already bound
                    if hasattr(self, "sock"):
                        self.sock.close()

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

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.sock.bind(("", self.clientPort))

    def sendRequest(self, mode, filename, options={}):
        """Sends RRQ or WRQ to server"""

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

        for key in options:
            packet += (
                key.encode("utf-8")
                + b"\x00"
                + str(options[key]).encode("utf-8")
                + b"\x00"
            )

        self.sock.sendto(packet, (self.destIP, self.destReqPort))

    def awaitAck(self):
        try:
            # listen for packet
            self.sock.settimeout(5)
            data, server = self.sock.recvfrom(512)

            dataParsed = packets.parseData(data)
            dataParsed["transferPort"] = server[1]

            return dataParsed
        except Exception as err:
            print("[212]: ", err)

    def sendAck(self, blockNumber: int, transferPort: int):
        """Sends an acknowledgment to the server"""
        packet = b"\x00\x04" + blockNumber.to_bytes(2)
        self.sock.sendto(packet, (self.destIP, transferPort))

    def receiveFile(self, blksize) -> bytes | None:
        """Listens for UDP packets containing file data"""

        # have a list of the previous blocks
        # for duplicate detection and reordering
        uniquePackets = []
        
        # keep track of timeouts
        numTimeouts = 0

        # this variable becomes true when the last packet comes in
        # while there are potentially other packets still being sent
        checkOrder = False

        while True:
            try:
                # 5 second time-out
                self.sock.settimeout(5)
                # 4 bytes = 2-byte opcode + 2-byte block number
                data, server = self.sock.recvfrom(blksize + 4)

                transferPort = server[1]

                data = packets.parseData(data)

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
                        self.sendAck(data["block"], transferPort)

                        # reset number of timeouts
                        numTimeouts = 0

                        # See RFC 1350, sec. 6 for termination process
                        # The extra stuff here is to acccount for out of sequence packet arrival
                        if len(data["data"]) != blksize or checkOrder:
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
                    packets.printError(data)
                    return None

            except TimeoutError:
                # Retransmit ACK if no subsequent DATA packet is received, otherwise break
                if data and data["opcode"] == 3 and numTimeouts < 5:
                    self.sendAck(data["block"], transferPort)
                    numTimeouts += 1
                else:
                    return None
                pass
            except ConnectionResetError:
                print("Server connection lost, check if tftp server running")
                break
            except Exception as err:
                print(f"[272 {type(err).__name__}]: {err}")
                break

        if len(uniquePackets) == 0:
            print("ERROR: File cannot be retrieved")
            return None

        # Sort data by block sequence number
        uniquePackets.sort(key=lambda data: data["block"])

        # join blocks together
        fileData = b"".join(list(map(lambda packet: packet["data"], uniquePackets)))

        return fileData

    def sendFile(self, filecontent: list[dict[int, bytes]]) -> None:
        """Sends split file contents into packets to the server"""

        sentBlocks = []

        def sendBlock(blockNumber: int, data: bytes, transferPort: int) -> None:
            """Sends a block to the server"""
            try:
                packet = b"\x00\x03" + blockNumber.to_bytes(2) + data
                self.sock.sendto(packet, (self.destIP, transferPort))
            except Exception as e:
                print(e)

        numTimeouts = 0

        # Send the first block as that was handled before this function was called
        sendBlock(1, filecontent[1], transferPort)

        while True:
            try:
                # 1 second time-out
                self.sock.settimeout(1)

                # listen for ACKs and ERRORs
                data, server = self.sock.recvfrom(DATALENGTH + 4)
                transferPort = server[1]

                if data:
                    data = packets.parseData(data)
                else:
                    continue

                match data["opcode"]:
                    case 4:
                        # Skip duplicate ACKs
                        if data["block"] in sentBlocks:
                            print(
                                f"Duplicate ACK found; Block Num: {data["block"]}"
                            )  # DEBUG ONLY
                            continue

                        print(f"ACK: Block {data["block"]}")  # DEBUG ONLY

                        # Add block number to list of sent blocks
                        sentBlocks.append(data["block"])

                        nextBlock = data["block"] + 1

                        if nextBlock in filecontent:
                            sendBlock(nextBlock, filecontent[nextBlock], transferPort)
                        elif (
                            filecontent[nextBlock - 1]
                            and len(filecontent[nextBlock - 1]) == 512
                        ):
                            # If the last block is exactly 512 bytes, send an empty block to signal the end of the file
                            sendBlock(nextBlock, b"", transferPort)
                        else:
                            print("File sent successfully!")
                            return
                    case 5:
                        packets.printError(data)
                        return
                    # OACK should already be handled in the initial request
                    case 6:
                        if "blksize" in data["options"]:
                            DATALENGTH = data["options"]["blksize"]
                            print(f"Block size set to {DATALENGTH}")

            except ConnectionResetError:
                # idk why or how this exception is even possible in UDP but it is
                print("Server connection lost")
                break

            except TimeoutError:
                # Retransmit block if no ACK is received, otherwise break
                if data and data["opcode"] == 4 and numTimeouts < 5:
                    print(f"TIMEOUT: Resending block {data["block"] + 1}")
                    sendBlock(filecontent[data["block"] + 1], transferPort)
                    numTimeouts += 1
                else:
                    break
            except Exception as e:
                break


if __name__ == "__main__":
    host = socket.gethostbyname(socket.gethostname())
    misc.onStart()

    if len(sys.argv) > 1 and sys.argv[1] == "-local":
        client = Client(host)
    else:
        client = Client()
