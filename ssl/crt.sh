# 生成 key
openssl genrsa -des3 -out server.key 1024
# 生成 csr
openssl req -new -key server.key -out server.csr
# 去除密码
openssl rsa -in server.key -out server_nopass.key
# 生成证书
openssl x509 -req -days 365 -in server.csr -signkey server_nopass.key -out server.crt