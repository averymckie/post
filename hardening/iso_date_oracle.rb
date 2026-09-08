# Independent-runtime oracle: reads one date or timestamp with Ruby's Date.parse and prints the calendar
# date it denotes and that date's Julian day number.
# Usage: ruby iso_date_oracle.rb '<date or timestamp>'
require 'date'
day = Date.parse(ARGV[0])
puts day.strftime('%Y-%m-%d')
puts day.jd
