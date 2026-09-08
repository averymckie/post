// Independent-runtime oracle: parses one JSON document with this runtime's own JSON.parse and prints
// one member of it. A document this parser refuses leaves an uncaught SyntaxError and a non-zero exit.
// Usage: node json_number_oracle.js '<json document>' '<member name>'
const [document, name] = process.argv.slice(2);
console.log(String(JSON.parse(document)[name]));
