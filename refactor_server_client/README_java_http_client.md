# Java HTTP Client for Django API

This directory contains a simple Java-based HTTP client designed to interact with a local Django web server. It uses the standard `java.net.http.HttpClient` (available in Java 11+) to send a GET request and retrieve a JSON response, requiring no external dependencies.

## Prerequisites

* **Java 11 or higher** must be installed and available in your system's PATH.
* The **Django backend server** must be running locally on port 8000 and listening at the `/getJSonValue` endpoint.

## Project Structure

* `refactor/java/client/MainHTTPClient.java`: The Java source code containing the HTTP client logic.
* `run-java-client.sh`: A bash automation script that compiles the Java source file and executes the compiled class.

## Usage

To build and run the client, simply execute the provided bash script from the root of this directory:

```bash
./run-java-client.sh
```

*(Note: If you receive a "Permission denied" error, ensure the script is executable by running `chmod +x run-java-client.sh` first).*

## Expected Output

Upon successful execution, the console will display the compilation status, the HTTP response code, and the raw JSON response from the server:

```text
Compiling refactor/java/client/MainHTTPClient.java...
Compilation successful. Running the Java client...
--------------------------------------------------
Status Code: 200
JSON Response: {"status": "success", "message": "Hello, World! You passed the 'hello' parameter."}
--------------------------------------------------
```