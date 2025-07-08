#!/bin/bash
set -e  # Exit on error

echo "Generating TLS certificates with proper CA extensions..."

# Create directories
mkdir -p certs/{ca,server,client}

# Generate CA config file
cat > ca.cnf << 'EOL'
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_ca
prompt = no

[req_distinguished_name]
CN = MyCA

[v3_ca]
basicConstraints = critical,CA:TRUE
keyUsage = critical,keyCertSign,cRLSign
subjectKeyIdentifier = hash
EOL

# Generate CA
echo -n "  CA... "
openssl req -x509 -newkey rsa:2048 -nodes -days 3650 \
  -config ca.cnf \
  -keyout certs/ca/ca.key -out certs/ca/ca.crt >/dev/null 2>&1
echo "✓"

# Generate Server Cert
echo -n "  Server cert... "
openssl req -newkey rsa:2048 -nodes \
  -keyout certs/server/server.key -out certs/server/server.csr \
  -subj "/CN=localhost" >/dev/null 2>&1

openssl x509 -req -in certs/server/server.csr -CA certs/ca/ca.crt \
  -CAkey certs/ca/ca.key -CAcreateserial -out certs/server/server.crt \
  -days 365 -extfile <(echo "keyUsage = digitalSignature,keyEncipherment") >/dev/null 2>&1
echo "✓"

# Generate Client Cert
echo -n "  Client cert... "
openssl req -newkey rsa:2048 -nodes \
  -keyout certs/client/client.key -out certs/client/client.csr \
  -subj "/CN=client" >/dev/null 2>&1

openssl x509 -req -in certs/client/client.csr -CA certs/ca/ca.crt \
  -CAkey certs/ca/ca.key -out certs/client/client.crt \
  -days 365 -extfile <(echo "keyUsage = digitalSignature") >/dev/null 2>&1
echo "✓"

# Cleanup
rm -f ca.cnf certs/*/*.csr certs/ca/ca.srl

# Verify certificates
echo -n "Verifying... "
if openssl verify -CAfile certs/ca/ca.crt certs/server/server.crt >/dev/null && \
   openssl verify -CAfile certs/ca/ca.crt certs/client/client.crt >/dev/null; then
    echo "✓"
    echo "Successfully generated certificates:"
    echo "  CA:       certs/ca/ca.crt"
    echo "  Server:   certs/server/server.{crt,key}"
    echo "  Client:   certs/client/client.{crt,key}"
else
    echo "❌"
    echo "Certificate verification failed!"
    exit 1
fi
