// Independent-runtime oracle: renders one .docx template with docxtemplater 3.69.3 under node and
// writes the rendered package out. The arguments are the template path, the JSON object of values and
// the output path; the placeholders the template carries are docxtemplater's own single-brace form.
// Usage: node docx_template_oracle.js <template.docx> <values.json> <out.docx>
//        (with NODE_PATH pointing at the docxtemplater checkout)
const fs = require('fs');
const PizZip = require('pizzip');
const Docxtemplater = require('docxtemplater');
const zip = new PizZip(fs.readFileSync(process.argv[2], 'binary'));
const document = new Docxtemplater(zip, { paragraphLoop: true, linebreaks: true });
document.render(JSON.parse(fs.readFileSync(process.argv[3], 'utf8')));
fs.writeFileSync(process.argv[4], document.getZip().generate({ type: 'nodebuffer' }));
