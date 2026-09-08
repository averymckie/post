// Independent-runtime oracle: validates one RDF graph against one SHACL shapes graph with
// rdf-validate-shacl 0.6.5 under node and prints the report's conformance flag on the first line and
// the number of validation results on the second.
// Usage: node shacl_validate_oracle.js <shapes.ttl> <data.ttl>
const rdf = require('@zazuko/env-node').default;
const SHACLValidator = require('rdf-validate-shacl').default;
(async () => {
  const shapes = await rdf.dataset().import(rdf.fromFile(process.argv[2]));
  const data = await rdf.dataset().import(rdf.fromFile(process.argv[3]));
  const report = await new SHACLValidator(shapes, { factory: rdf }).validate(data);
  process.stdout.write(report.conforms + '\n' + report.results.length + '\n');
})();
