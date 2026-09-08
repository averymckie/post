// Independent-runtime oracle: parses one MIME message with mailparser 3.9.23 under node and prints
// what it read as JSON. The single argument is the path of the message file; the checksum of every
// attachment is computed by the library itself, asked for as SHA-256 through its checksumAlgo option.
// Usage: node mime_oracle.js <message file>  (with NODE_PATH pointing at the mailparser checkout)
const fs = require('fs');
const { simpleParser } = require('mailparser');
simpleParser(fs.readFileSync(process.argv[2]), { checksumAlgo: 'sha256' }).then((mail) => {
  process.stdout.write(JSON.stringify({
    subject: mail.subject ?? null,
    from: mail.from?.text ?? null,
    to: mail.to?.text ?? null,
    text: mail.text ?? null,
    attachments: mail.attachments.map((a) => ({ filename: a.filename ?? null, checksum: a.checksum }))
  }));
});
