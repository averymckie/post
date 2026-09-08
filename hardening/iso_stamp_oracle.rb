# Independent-runtime oracle: parses one ISO 8601 timestamp with Ruby's Time.iso8601 and prints four fields.
# Usage: ruby iso_stamp_oracle.rb '<timestamp>'
require 'time'
STDOUT.set_encoding('UTF-8')
stamp = Time.iso8601(ARGV[0].dup.force_encoding('UTF-8'))
puts stamp.strftime('%Y-%m-%dT%H:%M:%S')
puts stamp.usec
puts stamp.nsec
puts stamp.utc_offset
