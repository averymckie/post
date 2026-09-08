<?php
// Independent-runtime oracle: lists the entries of one OPC package with PHP's ZipArchive (libzip)
// and prints one entry name per line.
// Usage: php pptx_parts_oracle.php <path to .pptx>
$archive = new ZipArchive();
$archive->open($argv[1]);
for ($index = 0; $index < $archive->numFiles; $index++) { echo $archive->getNameIndex($index), "\n"; }
