# Independent-runtime oracle: prints the Unicode full case fold of one string, then its lowercase.
# The argument bytes are tagged as UTF-8 and the output stream is set to UTF-8 so the result does not
# depend on the locale the reader happens to run under.
# Usage: ruby case_fold_oracle.rb '<text>'
STDOUT.set_encoding('UTF-8')
text = ARGV[0].dup.force_encoding('UTF-8')
puts text.downcase(:fold)
puts text.downcase
