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


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        # decode request
        request = self.data.decode("utf-8").split("\n")
        request_head = request[0].split()

        if len(request_head) == 3:
            method, path, protocol = request_head
        else:
            print("request head parsing error: more than 3 params")
            self.__404_response()
            return

        # check path

        # TODO REMOVE OS

        path = "./www" + path
        path_status = self.__check_path(path)
        print(path)

        # handle request
        if not method.upper() == "GET":
            self.__405_response()
        elif path_status == self.__IS_FILE or path_status == self.__IS_DIR:
            try:
                data = self.__get_files(path, path_status)
            except FileNotFoundError:
                self.__404_response()
                return

            if path.endswith(".html") or path.endswith("/"):
                self.__200_response(data, self.__HTML_CONTENT)
            elif path.endswith(".css"):
                self.__200_response(data, self.__CSS_CONTENT)
            else:
                print("error: should never hit this")

        elif path_status == self.__BAD_PATH:
            self.__301_response(path)
        elif path_status == self.__FILE_NOT_FOUND:
            self.__404_response()
        else:
            print("error: this check should never be hit")
            self.__404_response()

    def __check_path(self, path: str):
        """
        Checks the type of the path.

        params
        path: the requested path

        returns: a predefined constant indicating the type of resource at the path
        """

        # TODO REMOVE OS
        # TODO make root www

        print(path)
        if not (path.endswith("/") or path.endswith(".html") or path.endswith(".css")):
            print("bad path redirecting")
            return self.__BAD_PATH
        if path.startswith("./www/../"):
            return self.__FILE_NOT_FOUND
        elif path.endswith(".css") or path.endswith(".html"):
            print("found file")
            return self.__IS_FILE
        elif path.endswith("/"):
            print("found dir")
            return self.__IS_DIR
        else:
            print("error: should never hit")
            return None

    def __get_files(self, path: str, path_type: int):
        """
        Retrieves data from files

        params
        path: the path data is being requested from
        path_type: whether the path is a file or a directory

        returns: the data at the path.
        """

        # TODO REMOVE OS.
        # TODO PROBABLY MERGE check_path into here
        # TODO make root www
        try:
            if path_type == self.__IS_FILE:
                with open(path, "r") as f:
                    data = f.read()
            elif path_type == self.__IS_DIR:
                with open(path + "index.html", "r") as f:
                    data = f.read()
            else:
                print("error: should never hit this check")

            return data
        except FileNotFoundError:
            print("raising file not found error internal")
            raise FileNotFoundError

    def __200_response(self, data: str, content_type: str):
        """
        Sends a 200 response with the data requested

        params
        data: the data at the requested URL
        content_type: value of the Content-Type header field
        """
        response = "HTTP/1.1 200 OK\r\nContent-Type: " + content_type + "\r\n\r\n" + data + "\r\n"
        print(response)
        self.request.sendall(bytearray(response, "utf-8"))
        print("done sending\n")

    def __301_response(self, path: str):
        """
        Sends a 301 response. Redirects to the same path with a "/" char appended

        params
        bad_path: the path recieved with the inital request
        """
        print("redirecting request originally to: " + path)
        path = path[5:] + "/"
        print("HTTP/1.1 301 Moved Permanently\r\nLocation: http://" + HOST + ":" + str(PORT) + path + "\r\n")
        self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\nLocation: http://" + HOST + ":" + str(PORT) + path + "\r\nConnection: close\r\n", "utf-8"))
        print("done sending\n")

    def __404_response(self):
        """
        Sends a 404 response
        """
        # TODO TEST
        print("404 Not Found")
        content = '<!DOCTYPE html><html><head><title>Deeper Example Page</title><meta http-equiv="Content-Type" content="text/html;charset=utf-8"/></head><body><p>Error: 404 Not Found response</p></body></html>'

        self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n" + content + "\r\n", "utf-8"))
        print("done sending\n")

    def __405_response(self):
        """
        Sends a 405 response
        """
        print("405 Method Not Allowed")
        self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allow\r\n", "utf-8"))
        print("done sending\n")

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
