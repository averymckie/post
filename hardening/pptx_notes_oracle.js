// Independent-runtime oracle: parses one .pptx with officeparser 7.8.0 under node and prints the
// abstract syntax tree it returns as JSON.
// Usage: node pptx_notes_oracle.js <path to .pptx>
const officeParser = require('officeparser');
const fs = require('fs');
(async () => {
  const ast = await officeParser.parseOffice(fs.readFileSync(process.argv[2]));
  process.stdout.write(JSON.stringify(ast));
})();
