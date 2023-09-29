#  coding: utf-8 
import socketserver
import re
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

    __IS_FILE = 0
    __IS_DIR = 1
    __BAD_PATH = 2
    __FILE_NOT_FOUND = 3

    # TODO IMPORTANT TEST LINUX
    
    # TODO SERVE FROM WWW
    # TODO REGECT NON GET 405 Method Not Allowed
    # TODO MIME TYPES FOR HTML, CSS
    # TODO RETURN index.html FROM DIRECTORIES (ie, end with /)
    # TODO IF NOT ENDING IN MIMETYPE OR /, 301 REDIRECT TO PATH WITH / END
    # TODO 404 NOT FOUND
    # TODO TEST WITH SCRIPT, FIREFOX, CHROMIUM 127.0.0.1:8080

    # NOTE probably optional, should check http

    def handle(self):
        """
        Handles any requests to the server
        """
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        # decode request
        request = self.data.decode("utf-8").split("\n")
        request_head = request[0].split()
        #print("\n" + request[0])

        if len(request_head) == 3:
            method, path, protocol = request_head
        else:
            print("request head parsing error: more than 3 params")

        path_status = self.__check_path(path) # TODO catch type errors with path argument

        # handle request
        if not method.upper() == "GET":
            self.__405_response()
        elif path_status == self.__IS_FILE:
            data = self.__get_files(path) # TODO ASSIGNMENT
            self.__200_response(data)   # TODO ADD BODY
        elif path_status == self.__IS_DIR:
            data = self.__get_files(path)
            self.__200_response(data)
        elif path_status == self.__BAD_PATH:
            self.__301_response(path) # TODO TEST
        elif path_status == self.__FILE_NOT_FOUND:
            self.__404_response() # TODO TEST
        else:
            print("error: this check should never be hit")

    def __check_path(self, path: str):
        """
        Checks if a requested path is valid and exists.

        params
        path: the requested path

        returns: a predefined constant indicating the status of the path
        """
        if not (path.endswith("/") or path.endswith(".html") or path.endswith(".css")):
            return self.__BAD_PATH
        elif not path[:4] == "/www":
            # TODO CHECK IF WE ONLY SERVE ./www
            return self.__FILE_NOT_FOUND
        elif os.path.isfile(path):
            return self.__IS_FILE
        elif os.path.isdir(path):
            return self.__IS_DIR
        else:
            return self.__FILE_NOT_FOUND

    def __get_files(self, path):
        """
        Retrieves data from files

        params
        path: the path data is being requested from

        returns: the data at the path.
        """
        pass

    def __200_response(self, data):
        """
        Sends a 200 response with the data requested

        params
        data: the data at the requested URL
        """
        response = b"HTTP/1.1 200 OK\r\n"
        # TODO DATA BODY, rest of header

    def __301_response(self, bad_path):
        """
        Sends a 301 response. Redirects to the same path with a "/" char appended

        params
        bad_path: the path recieved with the inital request
        """
        path = bad_path + "/"
        print("301 Moved Permanently:" + path)
        self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\nLocation: " + path + "\r\n"))

    def __404_response(self):
        """
        Sends a 404 response
        """
        # TODO TEST
        print("404 Not Found")
        self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n", "utf-8"))

    def __405_response(self):
        """
        Sends a 405 response
        """
        print("405 Method Not Allowed")
        self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allow\r\n", "utf-8"))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    with socketserver.TCPServer((HOST, PORT), MyWebServer) as server:

        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
