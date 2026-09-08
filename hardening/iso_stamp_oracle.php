<?php
// Independent-runtime oracle: parses one ISO 8601 timestamp with PHP's DateTimeImmutable and prints four fields.
// Usage: php iso_stamp_oracle.php '<timestamp>'
$stamp = new DateTimeImmutable($argv[1]);
echo $stamp->format('Y-m-d\TH:i:s'), "\n";
echo $stamp->format('u'), "\n";
echo $stamp->getOffset(), "\n";
echo $stamp->format('P'), "\n";
