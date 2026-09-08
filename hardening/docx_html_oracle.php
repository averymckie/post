<?php
/*
 * PHPWord oracle: converts one .docx to HTML with PHPWord's own Word2007 reader and its own HTML
 * writer, and prints the document on stdout.
 *
 * argv[1] is the path of the composer autoloader of the PHPWord checkout and argv[2] is the .docx to
 * read. The file parses argv, calls the library and prints; it performs no arithmetic and branches on
 * no value.
 *
 * Install:  COMPOSER_ALLOW_SUPERUSER=1 composer require phpoffice/phpword:1.4.0   (in ~/phpword-oracle)
 */
require $argv[1];
$document = \PhpOffice\PhpWord\IOFactory::load($argv[2], 'Word2007');
echo \PhpOffice\PhpWord\IOFactory::createWriter($document, 'HTML')->getContent();
