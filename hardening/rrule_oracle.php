<?php
// Independent-runtime oracle: expands an RRULE with php-rrule and prints one ISO date per line.
// Usage: php rrule_oracle.php '<RRULE string>' '<DTSTART yyyy-mm-dd>'
require '/home/user/rlanvin/php-rrule/src/RRuleInterface.php';
require '/home/user/rlanvin/php-rrule/src/RRuleTrait.php';
require '/home/user/rlanvin/php-rrule/src/RfcParser.php';
require '/home/user/rlanvin/php-rrule/src/RRule.php';
$rule = new RRule\RRule($argv[1], new DateTime($argv[2]));
foreach ($rule as $occurrence) { echo $occurrence->format('Y-m-d'), "\n"; }
