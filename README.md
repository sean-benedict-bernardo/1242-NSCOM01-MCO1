# 1241-NSCOM01-MCO1

**Project Specifications
**
Objectives:
This project is designed to supplement classroom instruction and provide hands-on experience with network protocols. By completing this project, students will:

Review and comprehend the detailed function and design of network protocols as described in Internet standards documents (RFCs).
Implement a working network application that adheres to Internet standards.
 

Background:
The Trivial File Transfer Protocol (TFTP) is a lightweight, UDP-based application layer protocol commonly used for transferring files within a Local Area Network (LAN). It is often employed to upload or download operating system images and configuration files to network appliances. Unlike TCP-based protocols, TFTP implements its own mechanisms for reliable and ordered data delivery.

The current version, TFTP v2, is defined in RFC 1350, with extensions for features like block size negotiation and transfer size communication documented in RFCs 2347, 2348, and 2349.

 

Project Requirements:
For this project, you will implement a TFTP client program that complies with the TFTP v2 protocol specifications. The program must meet the following requirements:

Programming Language
C, Java, or Python with socket programming
Use only a command-line interface (no GUI required)
Core Functionality
The client must allow the user to specify the server IP address.

Support both upload and download operations for binary files.

Upload: The client should be able to send any accessible file from the local machine to the TFTP server.

Download: The client should allow the user to specify the filename for saving the downloaded file locally.

Error Handling
Implement robust error handling for the following scenarios:

Timeout: Detect and handle unresponsive servers.

Duplicate ACK: Properly handle duplicate acknowledgments.

File not found: Prompt the user if the file is unavailable.

Provide test cases to demonstrate the implementation of these error-handling mechanisms

Implement option negotiation as per RFCs 2347, 2348, and 2349:

Block size negotiation (blksize): Allow the user to specify the transfer block size.
Transfer size communication (tsize): Communicate the file size to the server during uploads.
 

Evaluation Criteria
Your project will be evaluated based on the following criteria:

Functionality:

Correct implementation of upload and download operations.

Support for binary file transfers.

Error Handling:

Proper handling of timeouts, duplicate ACKs and file not found.

Submission of test cases demonstrating error-handling functionality.

Protocol Compliance:

Adherence to TFTP v2 specifications (RFC 1350).

Correct implementation of optional features (if attempted).

Code Quality:

Readable, well-structured, and modular code.

Adequate comments and documentation in the source code.

Clear instructions for building and running the program.

Deliverables
Submit the following by the deadline:

Source Code:

The complete source code for your TFTP client in zip file.

Documentation:

A README file containing:

Instructions for compiling and running the program.

A description of the implemented features and error-handling mechanisms.

Test cases and sample outputs demonstrating functionality.

 

Additional Notes
You may use any standard libraries or frameworks available in your chosen programming language (e.g., Python’s socket library, Java’s java.net package, or C’s sys/socket.h).

Ensure your program is platform-independent if using Python or Java.

Focus on writing clean, efficient, and well-documented code.

Up to two (2) students per group. Sign up for your group at the People tab.
Rubric:  NSCOM01_MP1_Rubric.xlsxDownload NSCOM01_MP1_Rubric.xlsx
Submission date: February  19, 2025 11:59PM via AnimoSpace

Demonstration date: TBA by each instructor
