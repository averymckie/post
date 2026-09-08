# Independent-runtime oracle: normalizes one string with Ruby's String#unicode_normalize, the pure-Ruby
# implementation in lib/unicode_normalize, and prints the normalized text as hex, its length in characters
# and its length in bytes. Text crosses in and out as hex so that nothing depends on the reader's locale.
# Usage: ruby unicode_normalize_oracle.rb '<nfc|nfd|nfkc|nfkd>' '<text as utf-8 hex>'
text = [ARGV[1]].pack('H*').force_encoding('UTF-8').unicode_normalize(ARGV[0].to_sym)
puts text.b.unpack1('H*')
puts text.length
puts text.bytesize
