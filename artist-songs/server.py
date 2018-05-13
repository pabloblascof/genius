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

    def html_builder (self, song_list):

        html = '<html><head>"<meta charset=\"UTF-8\">" <h1>Songs</h1></head><body style="background-color: white" >'
        for song in song_list:
            html += "<li style='height:50px'>"
            if song['header_image_thumbnail_url'].find('default cover') != -1:
                html += "<img align='left' height='50' width='50' src='" + song['header_image_thumbnail_url'] + "'>"
            html += "<a href='" + song['url'] + "'>" + "<h4>" + song['title'] + "</h4>" + "</li>"

        html += "</body></html>"

        return html

    # GET
    def do_GET(self):

        http_response_code = 200

        path = self.path

        if self.path == "/":
            with open("artist.html") as f:
                message = f.read()
                self.wfile.write(bytes(message, "utf8"))
                print (path)

        elif 'searchSongs' in path:
            singer = self.path.split("=")[1]
            song_list = self.get_songs(singer)
            if song_list:
                message = self.html_builder(song_list)
                self.wfile.write(bytes(message, "utf8"))
                
            else:
                with open("not_found.html") as f:
                    message = f.read()
                self.wfile.write(bytes(message, "utf8"))

        elif 'searchSongs' in self.path:
            param = self.path.split("?")[1]
            artist_name = param.split("=")[1]
            song_list = self.get_songs(artist_name)
            if song_list:
                http_response = self.html_builder(song_list)
            else:
                http_response = "<h1>No songs found for %s</h1>" % artist_name
        else:
            http_response_code = 404

        # Send response status code
        self.send_response(http_response_code)

        # Send extra headers headers

        # Send the normal headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Write content as utf-8 data
        self.wfile.write(bytes(http_response, "utf8"))
        return


GeniusHandler.api_token = sys.argv[1]

httpd = socketserver.TCPServer(("", PORT), GeniusHandler)
print("serving at port", PORT)
httpd.serve_forever()