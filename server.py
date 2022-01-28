#  coding: utf-8 
import socketserver
import os.path

# Copyright 2022 Abram Hindle, Eddie Antonio Santos, Anisha Sethumadhavan
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
#
# Other references:
# eumiro, 30 June 2011, CC BY-SA 3.0, https://stackoverflow.com/a/6531678
# Rilwan, 7 November 2020, CC BY-SA 4.0, https://stackoverflow.com/a/64730825
# Andrew Clark, 12 June 2013, CC BY-SA 3.0, https://stackoverflow.com/a/17068310
# Bigyan Karki, CMPUT 404 LAB 2, 17 January 2022, https://drive.google.com/file/d/1TD8UR9o-GPaudPNsY9HrePzroRBsEBFe/view
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        '''
        Handles all the requests made by the client
        '''

        possible_reponses = {
            "200": "HTTP/1.1 200 OK\r\n",
            "301": "HTTP/1.1 301 Moved Permanently\r\n",
            "404": "HTTP/1.1 404 Path Not Found\r\n",
            "405": "HTTP/1.1 405 Method Not Allowed\r\n"
        }

        self.data = self.request.recv(1024).strip()
        print("Got a request of: %s\n" % self.data)
        request = self.data.split()
        print(request)

        # Check for proper request
        if len(request) == 0 or len(request) < 2:
            self.request.sendall((possible_reponses["405"] + "\r\n").encode())
            return

        r_method = request[0].decode()  # request method
        r_url = request[1].decode()     # request URL
        f_url = "./www"+r_url           # file URL

        # mime-types for CSS and HTML file
        if f_url.endswith(".css"):
            mime_type = "text/css"
        elif f_url.endswith(".html"):
            mime_type = "text/html"
        else:
            mime_type = "text"

        # to check for methods that can't be handled
        if r_method != "GET":
            self.request.sendall((possible_reponses["405"] + "\r\n").encode())
            return
        if '../' in f_url:
            self.request.sendall((possible_reponses["404"] + "\r\n").encode())
            return

        # to serve files from ./www or from directories(paths that end in /)
        if os.path.exists(f_url):
            if os.path.isfile(f_url):
                content = self.get_content(f_url)
                self.request.sendall((possible_reponses["200"] + "Content-Type: " + mime_type + "\r\n\r\n"
                                      + "".join(content)).encode())
            elif os.path.isdir(f_url):
                if f_url.endswith('/'):
                    path = f_url + "index.html"
                    content = self.get_content(path)
                    self.request.sendall((possible_reponses["200"] + "Content-Type: text/html\r\n\r\n"
                                          + "".join(content)).encode())
                else:
                    path = f_url + "/index.html"
                    content = self.get_content(path)
                    self.request.sendall((possible_reponses["301"] + 'http://localhost:8080/www' + r_url + "/"
                                          + "\r\nContent-Type: text/html\r\n\r\n"
                                          + "".join(content)).encode())
        else:
            self.request.sendall((possible_reponses["404"] + "\r\n").encode())

    def get_content(self, f_path):
        '''
        To get the contents of a file at the specified path
        :param f_path: file path/url
        :return: the content of the file
        '''

        try:
            f = open(f_path, "r")
            content = f.readlines()
            return content

        except Exception as e:
            return "Can't read the file"


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
