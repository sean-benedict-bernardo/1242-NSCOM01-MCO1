"""
TFTPv2 Client Implementation
as defined by RFC 1350

NSCOM01 S13
Strebel, Adler Clarence E.
Bernardo, Sean Benedict G.
"""

# Custom imports
import tftp_files, tftp_misc, tftp_packets

# Python imports
import socket, sys, random, time

# IP, PORT = "127.0.0.1", 69


class Client:
    def __init__(self, destIP: str = None):
        self.destIP = self.setDestination() if destIP == None else destIP

        # A requesting host chooses its source TID as described
        # above, and sends its initial request to the known TID
        # 69 decimal (105 octal) on the serving host.
        self.destReqPort = 69  # but also nice
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # as per clarification, this does not need to be reset
        # for every file transfer but only on program run
        self.clientPort = self.setOpenPort()

        # bind client socket to start sending packets
        self.setSocket()

        # client loop
        self.loop()

    def __del__(self):
        # Ensure that the socket is closed when the client is deleted
        if hasattr(self, "sock"):
            self.sock.close()

    def loop(self):
        """Main loop for the client"""

        def opDownload() -> None:
            # Download File
            try:
                # standard block size
                blksize = 512

                # prompt filename
                filename = tftp_misc.getInput("Enter filename to retrieve: ")

                # append options
                options = tftp_packets.appendOptions("RRQ")

                self.sendRequest("RRQ", filename, options)

                ackInit = None

                # await OACK, skip if no options because
                # regular unoptioned TFTP will immediately send DATA
                if len(options) > 0:
                    ackInit = self.awaitAck()

                    if ackInit == None:
                        return

                    if ackInit["opcode"] == 5:
                        tftp_packets.printError(ackInit)
                        print("File cannot be retrieved")
                        return

                    if ackInit["opcode"] == 6:
                        if "blksize" in ackInit["options"]:
                            blksize = ackInit["options"]["blksize"]
                            print(f"Block size set to {blksize}")
                        if "tsize" in ackInit["options"]:
                            print(f"Incoming file size: {ackInit["options"]["tsize"]}")

                        # Send ACK for OACK
                        self.sendAck(0, ackInit["transferPort"])

                fileData = self.receiveFile(
                    blksize, ackInit["transferPort"] if ackInit else None
                )

                if fileData:
                    tftp_files.writeFile(filename, fileData)
                    print(f"{filename} was retrieved successfully\n")
                else:  # File cannot be retrieved
                    print(f"{filename} cannot be retrieved\n")
            except Exception:
                # file cannot be retrieved
                pass

        def opUpload() -> None:

            # Send File
            try:
                blksize = 512
                filename = tftp_misc.getInput("Enter filename to upload: ")

                ackInit = None

                if not tftp_files.fileExists(filename):
                    print(f'File "{filename}" not found\n')
                    return

                # Can specify filename to be used on server when uploading
                filenameServer = tftp_misc.getInput(
                    "Enter filename to be used on server [Enter to default]: "
                )
                # Defaults to filename on client if no server filename is specified
                if not filenameServer or filenameServer == "":
                    filenameServer = filename

                # append options
                options = tftp_packets.appendOptions("WRQ")

                # send request
                self.sendRequest("WRQ", filenameServer, options)
                # await request
                ackInit = self.awaitAck()

                if ackInit == None:
                    return

                # no additional behavior for opcode 4

                if ackInit["opcode"] == 5:
                    tftp_packets.printError(ackInit)
                    return

                if ackInit["opcode"] == 6:
                    if "blksize" in ackInit["options"]:
                        blksize = ackInit["options"]["blksize"]
                        print(f"Receiving block size set to {blksize} bytes")
                    if "tsize" in ackInit["options"]:
                        tsize = ackInit["options"]["tsize"]
                        print(f"To be sent: {tsize} bytes")

                try:
                    fileContent = tftp_files.readFile(filename, blksize)
                except Exception as e:
                    print(e)
                    return

                self.sendFile(ackInit["transferPort"], fileContent, blksize)

            except FileNotFoundError:
                print(f'File "{filename}" not found')
            except:
                pass

        def opChangeDest() -> None:
            """Allows client to change destination server IP address after startup"""
            if hasattr(self, "sock"):
                self.sock.close()

            self.destIP = self.setDestination()

        while True:
            print("=============== TFTPv2 Client ===============")
            print(
                f"Client IP Addr:       {socket.gethostbyname(socket.gethostname())}:{self.clientPort}\n"
                + f"Destination IP Addr.: {self.destIP}\n"
            )
            userInput = int(
                tftp_misc.getInput(
                    f"What would you like to do",
                    ["Download File", "Upload File", "Change TFTP Server IP", "Exit"],
                )
            )

            match userInput:
                case 0:
                    opDownload()
                case 1:
                    opUpload()
                case 2:
                    opChangeDest()
                case 3:
                    print("\nExiting...\n")
                    return

    def setDestination(self):
        """Set destination IPv4 address with checks for valid IP address"""

        while True:
            localIP = tftp_misc.getInput("Enter destination IP address: ")

            # resolve localhost to loopback
            if localIP == "localhost":
                return "127.0.0.1"

            octets = localIP.split(".")

            # check if there is a valid number of octets
            if len(localIP.split(".")) != 4:
                print("Invalid IP")
                continue

            # check each octet if correct
            for octet in octets:
                if not octet.isdigit() or int(octet) < 0 or int(octet) > 255:
                    print("Invalid IP")
                    continue
            return localIP

    def setOpenPort(self):
        """Selects an open port for datas"""
        # see RFC 6335 for dynamic port range
        # tl;dr: ports in this range are not to be reserved at IANA
        # so we'll use this port for transfer port
        portMin, portMax = 49152, 65565

        while True:
            candidatePort = random.randint(portMin, portMax + 1)

            # https://stackoverflow.com/a/19196218
            result = self.sock.connect_ex(("127.0.0.1", candidatePort))
            if result == 0:
                return candidatePort

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

    def awaitAck(self) -> dict | None:
        try:
            # listen for packet
            self.sock.settimeout(5)
            data, server = self.sock.recvfrom(512)

            dataParsed = tftp_packets.parseData(data)
            dataParsed["transferPort"] = server[1]

            return dataParsed
        except ConnectionResetError:
            print("Server connection lost, ensure TFTP server is active")
            return None
        except socket.timeout:
            print("Connection timed out, ensure TFTP server is active")
            return None
        except Exception as err:
            print(f"[212 {type(err).__name__}]: ", err)

    def sendAck(self, blockNumber: int, transferPort: int):
        """Sends an acknowledgment to the server"""
        packet = b"\x00\x04" + blockNumber.to_bytes(2)
        self.sock.sendto(packet, (self.destIP, transferPort))

    def sendError(self, transferPort: int, errcode: int = 0):
        """Send error to server with unidentified transfer ID"""

        packet = (
            b"\x00\x05"
            + errcode.to_bytes(2)
            + tftp_packets.ERRORCODES[errcode]
            + b"\x00"
        )

        self.sock.sendto(packet, (self.destIP, transferPort))
        pass

    def receiveFile(
        self, blksize: int, initialTransferPort: int = None
    ) -> bytes | None:
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

                if initialTransferPort == None:
                    # Set initial transfer port if first
                    # DATA is first response from server
                    initialTransferPort = server[1]
                elif transferPort != initialTransferPort:
                    # "If a source TID does not match,
                    # the packet should be discarded as
                    # erroneously sent from somewhere else."

                    # *do nothing to discard*

                    # An error packet should be sent to the
                    # source of the incorrect packet...
                    self.sendError(transferPort, 5)
                    # while not disturbing the transfer
                    continue

                data = tftp_packets.parseData(data)

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
                    tftp_packets.printError(data)
                    return None

            except socket.timeout:
                # Retransmit ACK if no subsequent DATA packet is received, otherwise break
                if data and data["opcode"] == 3 and numTimeouts < 5:
                    self.sendAck(data["block"], transferPort)
                    numTimeouts += 1
                else:
                    return None
                pass
            except ConnectionResetError:
                print("Server connection lost, ensure TFTP server is active")
                return None
            except Exception:
                # something went wrong
                return None

        if len(uniquePackets) == 0:
            return None

        # Sort data by block sequence number
        uniquePackets.sort(key=lambda data: data["block"])

        # join blocks together
        fileData = b"".join(list(map(lambda packet: packet["data"], uniquePackets)))

        return fileData

    # Note to self: figure out why tf there's a seperate
    # ACK packet being received regardless of optioned or not optioned
    def sendFile(
        self,
        initialTransferPort: int,
        filecontent: dict[int, bytes],
        transferSize=512,
    ) -> None:
        """Sends split file contents into packets to the server"""

        sentBlocks = []

        def sendBlock(blockNumber: int, data: bytes, transferPort: int) -> None:
            """Sends a block to the server"""
            try:
                packet = b"\x00\x03" + blockNumber.to_bytes(2) + data
                self.sock.sendto(packet, (self.destIP, transferPort))
            except Exception as e:
                raise e

        # Send the first block as that was handled before this function was called
        sendBlock(1, filecontent[1], initialTransferPort)

        while True:
            try:
                # 1 second time-out
                self.sock.settimeout(1)

                # Testcase: add delay to account for duplicate packets
                # time.sleep(1)

                # listen for ACKs and ERRORs
                # 512 cuz why not lol
                data, server = self.sock.recvfrom(512)
                transferPort = server[1]

                if initialTransferPort == None:
                    # Set initial transfer port if first
                    # DATA is first response from server
                    initialTransferPort = transferPort
                elif transferPort != initialTransferPort:
                    # "If a source TID does not match,
                    # the packet should be discarded as
                    # erroneously sent from somewhere else."

                    # *do nothing to discard*

                    # An error packet should be sent to the
                    # source of the incorrect packet...
                    self.sendError(transferPort, 5)
                    # while not disturbing the transfer
                    continue  # aka we skip to the next packet

                if data:
                    data = tftp_packets.parseData(data)
                else:
                    continue

                match data["opcode"]:
                    case 4:
                        # Skip duplicate ACKs
                        if data["block"] in sentBlocks or data["block"] == 0:
                            print(f"Duplicate ACK found; Block Num: {data["block"]}")
                            # DEBUG ONLY
                            continue

                        # print(f"ACK: Block {data["block"]}")  # DEBUG ONLY

                        # Add block number to list of sent blocks
                        sentBlocks.append(data["block"])

                        nextBlock = data["block"] + 1

                        if nextBlock in filecontent:
                            sendBlock(nextBlock, filecontent[nextBlock], transferPort)
                        elif (
                            nextBlock - 1 in filecontent
                            and len(filecontent[nextBlock - 1]) == transferSize
                        ):
                            # If the last block is exactly transferSize bytes, or transferSize, send an empty block to signal the end of the file
                            sendBlock(nextBlock, b"", transferPort)
                        else:
                            print("File sent successfully!\n")
                            return
                    case 5:
                        tftp_packets.printError(data)
                        return

            except ConnectionResetError:
                print("Server connection lost, ensure TFTP server is active")
                break
            except socket.timeout:
                # Retransmit block if no ACK is received, otherwise break
                if data and data["opcode"] != 4 or numTimeouts < 5:
                    print(f"TIMEOUT: Resending block {data["block"] + 1}")
                    sendBlock(filecontent[data["block"] + 1], transferPort)
                    numTimeouts += 1
                else:
                    print("Timed out")
                    break
            except Exception:
                break


if __name__ == "__main__":
    host = socket.gethostbyname(socket.gethostname())
    tftp_misc.onStart()

    if len(sys.argv) > 1 and sys.argv[1] == "-local":
        client = Client(host)
    elif len(sys.argv) > 1 and sys.argv[1] == "-t":
        client = Client("192.168.254.113")
    else:
        client = Client()
