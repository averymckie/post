<?php
// Independent-runtime oracle: applies one relative modifier with PHP's DateTime::modify and prints one ISO date.
// Usage: php month_offset_oracle.php '<yyyy-mm-dd>' '<relative modifier>'
$date = new DateTime($argv[1]);
$date->modify($argv[2]);
echo $date->format('Y-m-d'), "\n";
