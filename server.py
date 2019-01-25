#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


# Things I have imported
import os
from pathlib import Path

# Resources I have used
# https://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-without-exceptions
# https://www.systutorials.com/241539/how-to-get-the-file-extension-from-a-filename-in-python/
# https://www.tutorialspoint.com/http/http_responses.htm


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.string_data = self.get_string_data()

        self.method = self.string_data[0][0]
        self.file = self.string_data[0][1]
        self.proto = self.string_data[0][2]

        self.check_method()
        self.check_file()

    # Parse client information and store it appropriately into a list
    def get_string_data(self):
        
        string_list = []
        string = self.data.decode().split("\r\n")
        
        for element in string:
            string_list.append(element.split(" "))

        return string_list 

    # Verify that we are only receiving a GET method
    def check_method(self):
        if self.method != "GET":
            status_code = " 405 Method Not Allowed\r\n"
            self.send_request(status_code, self.get_mime_type(), self.get_content(status_code))

    # Check if file exists, is a file and whether or not it is in the correct directory
    def check_file(self):
        path = os.path.abspath(os.getcwd() + "/www" + self.file)

        if self.file[-1] == "/":
            path += "/index.html"

        if Path(path).exists() and "www" in path:
            if Path(path).is_file():
                content = open(path).read()
                status_code = " 200 OK\r\n"
                self.send_request(status_code, self.get_mime_type(), content)
            else:
                status_code = " 301 Moved Permanently"
                self.send_request(status_code, self.get_mime_type(), self.get_content(status_code))
        
        else:
            status_code = " 404 Error Not Found\r\n"
            self.send_request(status_code, self.get_mime_type(), self.get_content(status_code))

    # Get the mime type
    def get_mime_type(self):
        _, ext = os.path.splitext(self.file)

        if ext == ".css":
            return "Content-Type: text/css\r\n"
        elif ext == ".html":
            return "Content-Type: text/html\r\n"
        else:
            return "Content-Type: text/html\r\n"

    # Construct the corresponding HTML given a status code
    def get_content(self, status_code):
        if status_code == " 301 Moved Permanently":
            contents = "<html> <head> \r\n" + \
                    "<title>301 Moved Permanently</title> \r\n" + \
                    "</head><body> \r\n" + \
                    "<h1>301 Moved Permanently</h1>\r\n" + \
                    "</body></html>\r\n"
            return contents
        elif status_code == " 404 Error Not Found\r\n":
            contents = "<html> <head> \r\n" + \
                    "<title>404 Not Found</title> \r\n" + \
                    "</head><body> \r\n" + \
                    "<h1>404 Not Found</h1>\r\n" + \
                    "</body></html>\r\n"
            return contents
        elif status_code == " 405 Method Not Allowed\r\n":
            contents = "<html> <head> \r\n" + \
                    "<title>405 Method Not Allowed</title> \r\n" + \
                    "</head><body> \r\n" + \
                    "<h1>405 Method Not Allowed</h1>\r\n" + \
                    "</body></html>\r\n"
            return contents

    # Construct and send the request        
    def send_request(self, status_code, mime_type, content):
        response = self.proto + status_code + mime_type + "\r\n" + content
        self.request.sendall(response.encode())

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()