# 1241-NSCOM01-MCO1
A simple TFTP client implementation in Python 3 in fulfillment of MCO1 for NSCOM01.

## Authors
Sean Benedict Bernardo
Adler Clarence Strebel


# Running the program
1. Run the client with `python tftp_client.py`.
2. Follow instructuions as displayed in program.

## Features
- Upload and download operations for binary files
- Negotiation of block size and transfer size as per RFCs 2347, 2348, and 2349
- Error handling for timeouts, duplicate ACKs, and file not found errors

## Longer description

The program binds a UDP socket to a dynamic client port, which connects to a specified TFTP server IP address. The RRQ (Read Request) operation supports option negotiation for block and transfer size, handling data by writing the received file to local storage. Similarly, WRQ (Write Request) allows writing to the TFTP server, with the option to specify a different filename. The client selects a transfer port from the dynamic port range (49152–65535), which is not reserved by IANA, ensuring compatibility with standard networking practices. ACK management ensures reliable file transfer by requiring the client to wait for an ACK packet (opcode 4) before sending the next block. Duplicate ACKs are discarded, and if no ACK is received after 1 second, the last sent block is retransmitted up to five times to prevent data loss.

The program includes robust error-handling mechanisms. Timeout handling (e.g., awaitAck) prevents the client from hanging indefinitely by limiting the wait time for responses. A ConnectionResetError detects when the server is unreachable, while a timeout error indicates that the server has stopped responding. The receiveFile function is responsible for processing read requests, receiving 512-byte data blocks, acknowledging packets, and ensuring correct file order and integrity. Meanwhile, the sendFile function transmits files by splitting them into 512-byte chunks and sending them block by block. Additional error handling includes detecting unknown ports (Error Code 5), managing duplicate ACKs, and identifying unexpected server disconnections. These features collectively ensure a reliable and efficient TFTP client.


## Error handling testcases instructions (a.k.a. How to recreate)

1. Timeout: Detect and handle unresponsive servers.
    - Run the client pointing to its IP address.
    - Ensure tftpd64 is not running
    - Windows will short circuit the attempted connection and display an error message.
    - If done with pointing to another computer, time out will occur as expected.

2. Duplicate ACK: Properly handle duplicate acknowledgments.
   - Add a short delay between receiving to sending packets
   - Watch the duplicate ACKs come in
   - Absolute cinema

3. File not found
   - Ensure tftpd64 is running
   - Run the client pointing to its IP address.
   - Ensure the file does not exist in the server's directory.
   - Attempt to retrieve said nonexistent file.
   - Server responds with error code 0x01.

## Test case outputs

1. Timeout (Local test, server is off)
```


TFTPv2 Client Implementation
by Bernardo and Strebel


=============== TFTPv2 Client ===============
Client IP Addr:       192.168.254.122:53039
Destination IP Addr.: 192.168.254.122

What would you like to do
[1] Download File
[2] Upload File
[3] Change TFTP Server IP
[4] Exit

> 1

Enter filename to retrieve:

> anotherfile.bin

What options would you like to append
[1] Block size
[2] Transfer Communication size
[3] None

> 3

Server connection lost, ensure TFTP server is active
anotherfile.bin cannot be retrieved

=============== TFTPv2 Client ===============
Client IP Addr:       192.168.254.122:53039
Destination IP Addr.: 192.168.254.122

What would you like to do
[1] Download File
[2] Upload File
[3] Change TFTP Server IP
[4] Exit

>
```

2. Duplicate ACK (delay set to 1s)
```


TFTPv2 Client Implementation
by Bernardo and Strebel


=============== TFTPv2 Client ===============
Client IP Addr:       192.168.254.122:60027
Destination IP Addr.: 192.168.254.122

What would you like to do
[1] Download File
[2] Upload File
[3] Change TFTP Server IP
[4] Exit

> 2

Enter filename to upload:

> FileB.bin

Enter filename to be used on server [Enter to default]:

> anotherfile.bin

What options would you like to append
[1] Block size
[2] Transfer Communication size
[3] None

> 1

Enter block size:

> 512

What options would you like to append
[1] Block size
[2] Transfer Communication size
[3] None

> 3

Receiving block size set to 512 bytes
Duplicate ACK found; Block Num: 3
Duplicate ACK found; Block Num: 4
Duplicate ACK found; Block Num: 5
Duplicate ACK found; Block Num: 6
Duplicate ACK found; Block Num: 7
Duplicate ACK found; Block Num: 8
File sent successfully!

=============== TFTPv2 Client ===============
Client IP Addr:       192.168.254.122:60027
Destination IP Addr.: 192.168.254.122

What would you like to do
[1] Download File
[2] Upload File
[3] Change TFTP Server IP
[4] Exit

>
```

3. File not found
```
TFTPv2 Client Implementation
by Bernardo and Strebel


=============== TFTPv2 Client ===============
Client IP Addr:       192.168.254.122:60878
Destination IP Addr.: 192.168.254.122

What would you like to do
[1] Download File
[2] Upload File
[3] Change TFTP Server IP
[4] Exit

> 1

Enter filename to retrieve:

> nonexistentfile.jpg

What options would you like to append
[1] Block size
[2] Transfer Communication size
[3] None

> 3

ERROR [0x01]: File not found.

nonexistentfile.jpg cannot be retrieved

=============== TFTPv2 Client ===============
Client IP Addr:       192.168.254.122:60878
Destination IP Addr.: 192.168.254.122

What would you like to do
[1] Download File
[2] Upload File
[3] Change TFTP Server IP
[4] Exit

>
```

## References
- [RFC 1350](https://tools.ietf.org/html/rfc1350)
- [RFC 2347](https://tools.ietf.org/html/rfc2347)
- [RFC 2348](https://tools.ietf.org/html/rfc2348)
- [RFC 2349](https://tools.ietf.org/html/rfc2349)
- [Answer to "Python send UDP packet"](https://stackoverflow.com/a/18746406)
- [Answer to "How to check if a network port is open?"](https://stackoverflow.com/a/19196218)