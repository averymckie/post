// Independent-runtime oracle: parses one HTML document with jsdom 30.0.1 under node -- a DOM
// implementation whose HTML parser is parse5, sharing no code with libxml2 or with html5lib -- and
// prints what that DOM reports about the document as one JSON object. The document arrives on stdin;
// argv[2] is the number of clicks to dispatch at the element with id "act". The shim only reads stdin
// and argv, calls the library and prints.
// Usage: node dom_page_oracle.js <clicks>  (with NODE_PATH pointing at the jsdom checkout)
const { JSDOM } = require('jsdom');
const chunks = [];
process.stdin.on('data', (chunk) => chunks.push(chunk));
process.stdin.on('end', () => {
  const dom = new JSDOM(Buffer.concat(chunks).toString('utf8'), { runScripts: 'outside-only' });
  const document = dom.window.document;
  const received = [];
  document.querySelectorAll('#act').forEach((button) => {
    button.addEventListener('click', (event) => received.push(event.type));
  });
  Array.from({ length: Number(process.argv[2]) }).forEach(() => {
    document.querySelectorAll('#act').forEach((button) => button.click());
  });
  process.stdout.write(JSON.stringify({
    rows: [...document.querySelectorAll('#data tbody tr')]
      .map((row) => [...row.querySelectorAll('td')].map((cell) => cell.textContent)),
    hidden: [...document.querySelectorAll('[hidden]')].map((element) => element.localName),
    scripts: [...document.querySelectorAll('script')].map((element) => element.localName),
    references: [...document.querySelectorAll('[src], [href]')]
      .map((element) => [element.localName, element.getAttribute('src'), element.getAttribute('href')]),
    boxes: [...document.querySelectorAll('#data tbody td')]
      .map((cell) => [cell.offsetWidth, cell.getBoundingClientRect().width]),
    lang: document.documentElement.getAttribute('lang'),
    events: received,
  }));
});
