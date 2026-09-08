# Independent-runtime oracle: parses one CSV file with Ruby's own CSV library and prints one
# tab-separated line per row -- each field either the four letters NULL, for the object CSV
# substitutes for a field with no text, or the letter S followed by the field's bytes as hex.
# Usage: ruby csv_field_oracle.rb <file.csv>
require 'csv'
STDOUT.set_encoding('UTF-8')
CSV.read(ARGV[0]).each do |row|
  puts row.map { |field| field.nil? ? 'NULL' : ('S' + field.unpack1('H*')) }.join("\t")
end
