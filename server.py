#  coding: utf-8 
import socketserver
import os

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


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("---Receive---\n{}\n".format(self.data))

        # Indicates a malformed request
        if not self.data:
            returnData = "HTTP/1.1 400 Bad Request"
            print("---Return---\n{}\n".format(returnData))
            self.request.sendall(returnData.encode())
            return

        # Get some info from the header and split it into chunks
        reqInfo = str(self.data, "utf-8").splitlines()[0].split(' ')

        # We only handle GET requests
        if not reqInfo[0] == "GET":
            returnData = "HTTP/1.1 405 Method Not Allowed"
            print("---Return---\n{}\n".format(returnData))
            self.request.sendall(returnData.encode())
            return

        # Start with the address we were given
        returnPath = reqInfo[1]

        # Use extensions to determine content types and whether something is
        # a file (redirect under assumption that extensionless path without
        # trailing slash was supposed to be a path)
        fileExt = os.path.splitext(returnPath)[1]

        # If we're looking in a folder without a file specified, return index.html
        if not fileExt:
            # Check for trailing slash, redirect if not present
            if returnPath[-1] == "/" or returnPath[-1] == "\\":
                returnPath += "index.html"
                fileExt = ".html"
            else:
                returnData = "HTTP/1.1 302 Found\r\n"
                returnData += "Location: {}".format(reqInfo[1] + '/')
                print("---Return---\n{}\n".format(returnData))
                self.request.sendall(returnData.encode())
                return

        # Prepend our folder last, and resolve relative pathing
        # solves other path resolution and security issues
        returnPath = "./www" + os.path.abspath(returnPath)
        print("PATH: {}".format(returnPath))

        # Content wasn't found at that path
        if not os.path.exists(returnPath) or not os.path.isfile(returnPath):
            returnData = "HTTP/1.1 404 Not Found"
            print("---Return---\n{}\n".format(returnData))
            self.request.sendall(returnData.encode())
            return
        
        # We're returning something, so request is good (need a quick check to see if we actually did a 302 redirect)
        returnData = "HTTP/1.1 200 OK\r\n"

        # HTML mime-type
        if fileExt.lower() == ".html":
            returnData += "Content-Type: text/html\r\n"
        # CSS mime-type
        elif fileExt.lower() == ".css":
            returnData += "Content-Type: text/css\r\n"
        # Treat everything else as text
        else:
            returnData += "Content-Type: text/plain\r\n"

        # Need a line break between header and content
        returnData += "\r\n"

        # Add file content to our return content
        indexFile = open(returnPath, "r")
        for line in indexFile:
            returnData += line

        print("---Return---\n{}\n".format(returnData))
        self.request.sendall(returnData.encode())

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True

    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    
    # interrupt the program with Ctrl-C
    server.serve_forever()
