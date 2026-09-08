// Independent-runtime oracle: renders one template with nunjucks configured to refuse an undefined
// variable, and prints the result. It exits non-zero when nunjucks refuses.
// Usage: node template_strict_oracle.js '<template>' '<json context>'
const nunjucks = require('nunjucks');
console.log(new nunjucks.Environment(null, { throwOnUndefined: true })
    .renderString(process.argv[2], JSON.parse(process.argv[3])));
