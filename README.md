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

## Error Handling testcases (a.k.a. How to recreate)

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


## References
- [RFC 1350](https://tools.ietf.org/html/rfc1350)
- [RFC 2347](https://tools.ietf.org/html/rfc2347)
- [RFC 2348](https://tools.ietf.org/html/rfc2348)
- [RFC 2349](https://tools.ietf.org/html/rfc2349)
- [Answer to "Python send UDP packet"](https://stackoverflow.com/a/18746406)
- [Answer to "How to check if a network port is open?"] https://stackoverflow.com/a/19196218