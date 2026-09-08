// Independent-runtime oracle: renders one template with nunjucks under its own default settings, then with
// autoescape turned off, and prints one line for each.
// Usage: node template_render_oracle.js '<template>' '<json context>'
const nunjucks = require('nunjucks');
const template = process.argv[2];
const context = JSON.parse(process.argv[3]);
console.log(new nunjucks.Environment().renderString(template, context));
console.log(new nunjucks.Environment(null, { autoescape: false }).renderString(template, context));
