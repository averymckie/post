// Independent-runtime oracle: resolves one reference against one base with the WHATWG URL parser and prints it.
// Usage: node url_resolve_oracle.js '<base>' '<reference>'
const [base, reference] = process.argv.slice(2);
console.log(new URL(reference, base).href);
