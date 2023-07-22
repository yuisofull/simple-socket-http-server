Chạy server:
```
python3 webserver.py <host> <port>
```

Tính năng Upload:
```
curl -H "File-Name: <tên file>" --data-binary @<đường dẫn tới file> <url>
```

File sẽ được lưu dưới tên file.
Tính năng Download:
```
curl <url>/<tên file vừa upload>
```

 -Hoặc lên browser và vô <url>/<tên file vừa upload>

===

Running the server:
```
python3 webserver.py <host> <port>
```

Upload feature:
```
curl -H "File-Name: <file name>" --data-binary @<file path> <url>
```
The uploaded file will be saved under the specified file name.

Download feature:
```
curl <url>/<uploaded file name>
```
Or you can open your browser and go to `<url>/<uploaded file name>` to download the file.
