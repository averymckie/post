<?php
// Independent-runtime oracle: hashes one hex-encoded artifact with PHP's own SHA-256 (ext/hash, not
// OpenSSL) and prints the digest as this runtime writes it.
// Usage: php sha256_oracle.php '<artifact bytes as hex>'
echo hash('sha256', hex2bin($argv[1])), "\n";
