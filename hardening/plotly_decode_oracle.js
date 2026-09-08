// Independent-runtime oracle: decodes one plotly typed-array specification with the decoder that
// ships in plotly.js 4.0.0, the JavaScript implementation plotly.py names in the page it writes.
// Reads the specification as JSON on argv and prints the constructor name of the array the library
// returns on the first line and one value per line after it.
// Usage: NODE_PATH=<prefix>/node_modules node plotly_decode_oracle.js '<json specification>'
const array = require('plotly.js/src/lib/array.js');
const decoded = array.decodeTypedArraySpec(JSON.parse(process.argv[2]));
process.stdout.write([decoded.constructor.name].concat(Array.from(decoded).map(String)).join('\n'));
