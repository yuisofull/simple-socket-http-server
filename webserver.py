import socket
import sys

HOST = int(sys.argv[1])
PORT = int(sys.argv[2])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
print(f'Server running on {HOST}:{PORT}')


s.listen(5)

while True:
    conn, addr = s.accept()
    while True:
        #while True:
        data = conn.recv(1000)
        if not data: break
        print(data.decode())
        request = data.split(b'\r\n')[0]
        req_method = request.split(b' ')[0]
        req_url = request.split(b' ')[1].strip(b'/')

        print(f"[*] Request from user: {request}")
        if req_method == b'GET':
            if req_url == b"":
                url = 'index.html'
                ctype = "text/html"
            elif req_url == b"favicon.ico": 
                url = req_url
                ctype = "image/x-icon"
            else:
                url = req_url
                ctype = "application/x-www-form-urlencoded"
            #stringdata = '<h1>' + data.decode() + '</h1>'
            #stringdata = stringdata.encode()
            with open(url, 'rb') as f:
                resdata = f.read()

        elif req_method == b'POST':
            des1 = data.decode().find('File-Name:')
            des2 = data.find(b'\r\n\r\n')
            filename = data.decode()[des1+11:].split('\n')[0]
            url = filename.strip('\n').strip('\r').strip('\r\n')
            resdata = resdata.decode()
            resdata = 'You have uploaded: '  + filename
            resdata = resdata.encode()
            ctype = "text/html"
            with open(url, 'w') as f:
                f.write(data[des2+4:].decode())
            resdata = data
        '''elif req_method == b'PUT':
            url = "index.html"
            ctype = "text.html"
            stringdata = 'You have PUT: '  + data.decode()
            stringdata = stringdata.encode()'''
        
        header  = "HTTP/1.1 200\r\n"
        header += f"Content-length: {len(resdata)}\r\n"
        header += f"Content-Type: {ctype}\r\n\r\n"

        response = header.encode() + resdata 
        conn.send(response)
        conn.close()
        break

