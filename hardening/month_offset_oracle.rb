# Independent-runtime oracle: shifts a date by whole months with Ruby's Date#>> and prints one ISO date.
# Usage: ruby month_offset_oracle.rb '<yyyy-mm-dd>' '<months>'
require 'date'
puts (Date.iso8601(ARGV[0]) >> ARGV[1].to_i).to_s
