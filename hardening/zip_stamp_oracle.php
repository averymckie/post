<?php
// Independent-runtime oracle: reads one ZIP archive with PHP's zip extension (libzip 1.7.3) and
// prints one tab-separated line per entry -- the entry name as hex, and the last-modified instant
// this runtime resolves the archive's MS-DOS date and time fields to, in seconds since the epoch.
// Usage: php zip_stamp_oracle.php <archive.zip>
$archive = new ZipArchive();
$archive->open($argv[1]);
for ($index = 0; $index < $archive->numFiles; $index++) {
    $stat = $archive->statIndex($index);
    echo bin2hex($stat['name']), "\t", $stat['mtime'], "\n";
}
