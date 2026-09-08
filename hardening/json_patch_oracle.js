// Independent-runtime oracle: computes the RFC 6902 patch between two JSON documents with
// fast-json-patch 3.1.1 under node and prints it as JSON. Standard input is a JSON array holding
// the two documents; standard output is the array of operations the library returns.
// Usage: node json_patch_oracle.js  (with NODE_PATH pointing at the fast-json-patch checkout)
const jsonpatch = require('fast-json-patch');
const chunks = [];
process.stdin.on('data', (chunk) => chunks.push(chunk));
process.stdin.on('end', () => {
  const pair = JSON.parse(Buffer.concat(chunks).toString('utf8'));
  process.stdout.write(JSON.stringify(jsonpatch.compare(pair[0], pair[1])));
});
