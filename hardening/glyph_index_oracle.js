// Independent-runtime oracle: maps each character of one string to its glyph index in one font file,
// with opentype.js under node, and prints one index per line.
// Usage: node glyph_index_oracle.js '<font path>' '<utf-8 text as hex>'
const opentype = require('opentype.js');
const fs = require('fs');
const [fontPath, hexText] = process.argv.slice(2);
const font = opentype.parse(fs.readFileSync(fontPath));
for (const character of Buffer.from(hexText, 'hex').toString('utf8')) {
    console.log(font.charToGlyphIndex(character));
}
