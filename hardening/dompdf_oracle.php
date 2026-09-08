<?php
/*
 * dompdf oracle: reads one HTML document on stdin and prints the rendered PDF as base64 on stdout.
 *
 * argv[1] is the path of the composer autoloader of the dompdf checkout. The file parses argv, calls the
 * library and prints; it performs no arithmetic and branches on no value.
 *
 * Install:  COMPOSER_ALLOW_SUPERUSER=1 composer require dompdf/dompdf:3.1.4   (in ~/dompdf-oracle)
 */
require $argv[1];
$html = stream_get_contents(STDIN);
$dompdf = new \Dompdf\Dompdf();
$dompdf->loadHtml($html);
$dompdf->render();
echo base64_encode($dompdf->output());
