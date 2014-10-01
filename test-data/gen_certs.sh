for x in 512 1024 2048 4096 8192 5777 1777
do
	for r in 1 2 3 4 5
	do
		name=${x}_${r}
		openssl genrsa -out "$name.pem" $x
		openssl rsa -in "$name.pem" -pubout -out "$name.pub"
		openssl req -new -key "$name.pem" -subj "/C=DE/ST=Hessen/L=Frankfurt/O=KeyCheck/OU=KeyCheckerTesting/CN=www.example.com" -out "$name.csr"
		openssl req -new -key "$name.pem" -x509 -days 2000 -subj "/C=DE/ST=Hessen/L=Frankfurt/O=KeyCheck/OU=KeyCheckerTesting/CN=www.example.com" -out "$name.cert"
	done
done