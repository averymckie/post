// Independent-runtime oracle: converts one HTML document to Markdown with turndown 7.2.4 under node
// and prints the result. The HTML arrives on stdin and the Markdown leaves on stdout.
// Usage: node html_markdown_oracle.js  (with NODE_PATH pointing at the turndown checkout)
const TurndownService = require('turndown');
const chunks = [];
process.stdin.on('data', (chunk) => chunks.push(chunk));
process.stdin.on('end', () => {
  process.stdout.write(new TurndownService().turndown(Buffer.concat(chunks).toString('utf8')));
});
