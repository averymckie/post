# Independent-runtime oracle: hashes one hex-encoded artifact with Ruby's own SHA-256
# (ext/digest/sha2, not OpenSSL) and prints the digest as this runtime writes it.
# Usage: ruby sha256_oracle.rb '<artifact bytes as hex>'
require 'digest'
puts Digest::SHA256.hexdigest([ARGV[0]].pack('H*'))
