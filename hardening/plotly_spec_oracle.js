// Independent-runtime oracle: asks plotly.js 4.0.0, the JavaScript implementation plotly.py names in
// the page it writes, whether one JSON value is a typed-array specification, and prints what the
// library answers. plotly.js reads a `window` global to tell a browser from its own test container
// (src/lib/is_plain_object.js), so the shim points it at the node global before requiring; nothing
// else is stubbed and no value is inspected here.
// Usage: NODE_PATH=<prefix>/node_modules node plotly_spec_oracle.js '<json value>'
globalThis.window = globalThis;
const array = require('plotly.js/src/lib/array.js');
process.stdout.write(String(array.isTypedArraySpec(JSON.parse(process.argv[2]))));
