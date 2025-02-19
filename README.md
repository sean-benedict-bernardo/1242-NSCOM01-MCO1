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
- [Answer to "How to check if a network port is open?"] https://stackoverflow.com/a/19196218