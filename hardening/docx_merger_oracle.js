// Independent-runtime oracle: composes several .docx files into one with docx-merger 1.2.2 under
// node and writes the result. The first path on the command line is the file to write; every path
// after it is a source document, in order, and the first of those is the merger's own master. The
// shim parses argv, reads the files as the library's README says to ("Read input files as binary and
// pass it to the `DocxMerger` constructor fuction as a array of files"), calls the library and writes
// what its save callback hands back. Nothing here parses, computes or branches on a document value.
// Usage: node docx_merger_oracle.js <out.docx> <first.docx> <second.docx> [...]
//        (with NODE_PATH pointing at the docx-merger checkout)
const fs = require('fs');
const DocxMerger = require('docx-merger');
const target = process.argv[2];
const sources = process.argv.slice(3).map((path) => fs.readFileSync(path, 'binary'));
const merger = new DocxMerger({}, sources);
merger.save('nodebuffer', (data) => fs.writeFileSync(target, data));
