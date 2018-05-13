import http.server
import socketserver
import http.client
import json
import sys

socketserver.TCPServer.allow_reuse_address = True

# -- IP and the port of the server
IP = "localhost"  # Localhost means "I": your local machine
PORT = 8000

class GeniusHandler(http.server.BaseHTTPRequestHandler):

    api_token = sys.argv[1]

    def send_query(self, query):

        print('Query :', query)
        headers = {"Authorization": "Bearer " + self.api_token}

        conn = http.client.HTTPSConnection("api.genius.com")
        conn.request("GET", query, None, headers)
        r1 = conn.getresponse()
        print(r1.status, r1.reason)
        res_raw = r1.read().decode("utf-8")
        conn.close()

        repos = json.loads(res_raw)
        return repos

    def get_songs(self, singer):

        song_list = []
        page = "/search?q=" + singer
        res_json = self.send_query(page)

        for item in res_json['response']['hits']:
            id = item['result']['primary_artist']['id']
            print('ID:',id)
            break

        if not id:
            return song_list

        page = "/artists/%s/songs?per_page=25&page=1" % (id)

        songs_res = self.send_query(page)

        song_list = songs_res['response']['songs']

        return song_list

        with open("songs.html", "w"):
            self.wfile.write(bytes('<html><head><h1>Songs</h1><body style="background-color: blue" >',"utf8"))

            for song in song_list:
                if 'default_cover' not in song['header_image_thumbnail_url']:
                    self.wfile.write(bytes("<li><img align='left' height='50' width='50' src='" + song['header_image_thumbnail_url'] + "'>"
                                           + "<a href='" + song['url'] + "'>" + "<h4>" + song['title'] + "</h4>" + "</li>"))
            self.wfile.write(bytes("</head></html>"))

    # GET
    def do_GET(self):

        def send_file(file): # call to enter a filename to be opened
            with open(file) as f:
                message = f.read()
            self.wfile.write(bytes(message, "utf8"))

        status_code = 200

        path = self.path

        if self.path == "/":
            with open("artist.html") as f:
                message = f.read()
            self.wfile.write(bytes(message, "utf8"))

        elif 'searchSongs' in path:

            singer= self.path.split("=")[1]
            song_list = self.get_songs(singer)
            if song_list:
                http_response = self.html_builder(song_list)
            else:
                http_response = "<h1>No songs found for %s</h1>" % singer

            send_file('list.html')
            self.wfile.write(bytes(http_response, "utf8"))
            return


        else:
            http_response_code = 404

        # Send response status code
        self.send_response(status_code)

        # Send extra headers headers

        # Send the normal headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(bytes(http_response, "utf8"))
        return


GeniusHandler.api_token = sys.argv[1]

httpd = socketserver.TCPServer(("", PORT), GeniusHandler)
print("serving at port", PORT)
httpd.serve_forever()