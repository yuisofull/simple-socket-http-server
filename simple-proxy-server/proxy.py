import socket
import sys
import threading

def send_response(conn, status_code, content_type, response_data):
    header = f"HTTP/1.1 {status_code}\r\n"
    header += f"Content-Length: {len(response_data)}\r\n"
    header += f"Content-Type: {content_type}\r\n\r\n"

    response = header.encode() + response_data
    conn.send(response)

def proxy(conn, proxy_url,data):
    request = data.split(b'\r\n')[0]
    http_pos = proxy_url.decode().find("://") # find pos of ://
    if (http_pos==-1):
        temp = proxy_url.decode()
    else:
        temp = proxy_url.decode()[(http_pos+3):] # get the rest of url
    port_pos = temp.find(":") # find the port pos (if any)
    # find end of web server
    webserver_pos = temp.find("/")
    if webserver_pos == -1:
        webserver_pos = len(temp)

    webserver = ""
    port = -1
    if (port_pos==-1 or webserver_pos < port_pos): 

        # default port 
        port = 80 
        webserver = temp[:webserver_pos] 
        tail = temp[webserver_pos:]
    else: # specific port 
        port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        webserver = temp[:port_pos] 
        tail = temp[webserver_pos:]
    sv = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    #s.settimeout(config['CONNECTION_TIMEOUT'])
    sv.connect((webserver, port))
    firstline = f"GET {tail} {request.split(b' ')[2].decode()}"
    headers = data.split(b'\r\n\r\n')
    temp = headers[0].split(b'\r\n')
    temp[0] = firstline.encode()
    temp = b'\r\n'.join(temp)+ b'\r\n'+ b'Connection: Close' + b"\r\n\r\n" +headers[1]
    #proxy_res= firstline.encode() + temp.encode()
    print(f"SERVER REQUEST: \n{temp.decode()}")
    sv.send(temp)
    while True:
        # receive data from web server
        res = sv.recv(4096)
        if (len(res)<=0): break
        print(f"SERVER RESPONES: \n{res.decode()}")
        conn.send(res) # send to browser/client   
    sv.close()
    conn.close()

def process_get_request(conn, req_url,data):
    req_url1 = req_url.strip(b'/')
    if req_url1 == b"":
        url = 'index.html'
        ctype = "text/html"
    elif req_url1 == b"favicon.ico":
        url = req_url1.decode()
        ctype = "image/x-icon"
    else:
        url = req_url1.decode()
        ctype = "application/x-www-form-urlencoded"

    try:
        with open(url, 'rb') as f:
            resdata = f.read()
    except IOError:
        # Handle proxy 
        proxy(conn, req_url,data)
        return ctype, b'', True

    return ctype, resdata, False

def process_post_request(conn, req_url, data):
    if req_url == b"submit":
        # Handle form submission
        try:
            post_data = data.split(b'\r\n\r\n', 1)[1]
            with open("post.txt", 'wb') as f:
                f.write(post_data)
            resdata = "success uploading".encode()
            ctype = "text/plain"
        except IOError:
            with open("error403.html", 'rb') as f:
                resdata = f.read()
            ctype = "text/html"
            send_response(conn, b"403 Forbidden", ctype, resdata)
            conn.close()
    elif req_url == b"upload":
        # Handle file upload 
        des1 = data.decode().find('File-Name:')
        des2 = data.find(b'\r\n\r\n')
        filename = data.decode()[des1 + 11:].split('\n')[0]
        url = filename.strip('\n').strip('\r').strip('\r\n')
        resdata = f'You have uploaded: {filename}'.encode()
        ctype = "text/plain"  # Set a generic Content-Type since it's a text response
        with open(url, 'wb') as f:  # Use 'wb' mode for writing binary data
            f.write(data[des2 + 4:])
        send_response(conn, b"403 Forbidden", ctype, resdata)
        conn.close()
    else:
        # Return a 403 Forbidden response for unknown POST requests
        with open("error403.html", 'r') as f:
            resdata = f.read()
        ctype = "text/html"
        send_response(conn, b"403 Forbidden", ctype, resdata.encode())
        conn.close()

def process(conn, addr):
    while True:
        data = conn.recv(4096)
        if not data:
            return

        print(data.decode())

        request = data.split(b'\r\n')[0]
        req_method = request.split(b' ')[0]
        req_url = request.split(b' ')[1]
        #proxy_url = request.split(b' ')[1]
        print(f"[*] Request from user: {addr}")
        proxy = False
        if req_method == b'GET':
            ctype, resdata, proxy = process_get_request(conn, req_url,data)
        elif req_method == b'POST':
            process_post_request(conn, req_url, data)
            return
        else:
            # Return a 403 Forbidden response for unsupported methods
            with open("error403.html", 'r') as f:
                resdata = f.read()
            ctype = "text/html"
            send_response(conn, b"403 Forbidden", ctype, resdata.encode())
            conn.close()
            return
        if proxy == False:    
            send_response(conn, b"200", ctype, resdata)
            conn.close()
        return

def main():
    if len(sys.argv) != 3:
        print("Usage: python server.py <HOST> <PORT>")
        sys.exit(1)

    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    print(f'Server running on {HOST}:{PORT}')

    s.listen(5)
    while True:
        client, caddr = s.accept()
        thread = threading.Thread(target=process, args=(client,caddr))
        thread.start()

if __name__ == "__main__":
    main()
