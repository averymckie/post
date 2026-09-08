<?php
// Independent-runtime oracle: reads one date or timestamp with PHP's DateTimeImmutable and prints the
// calendar date it denotes and the instant it denotes as this runtime counts it.
// Usage: php iso_date_oracle.php '<date or timestamp>'
$moment = new DateTimeImmutable($argv[1]);
echo $moment->format('Y-m-d'), "\n";
echo $moment->getTimestamp(), "\n";
