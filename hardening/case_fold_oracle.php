<?php
// Independent-runtime oracle: prints the Unicode full case fold of one string, then its lowercase.
// Usage: php case_fold_oracle.php '<text>'
echo mb_convert_case($argv[1], MB_CASE_FOLD, 'UTF-8'), "\n";
echo mb_strtolower($argv[1], 'UTF-8'), "\n";
