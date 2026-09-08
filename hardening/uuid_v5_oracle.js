// Independent-runtime oracle: computes one name-based UUID with the uuid package 14.0.2 under node
// and prints it. The name crosses as hex so that the shim decodes and does nothing else.
// Usage: NODE_PATH=<prefix>/node_modules node uuid_v5_oracle.js <namespace-uuid> <name-as-hex>
const { v5 } = require('uuid');
console.log(v5(Buffer.from(process.argv[3], 'hex').toString('utf8'), process.argv[2]));
