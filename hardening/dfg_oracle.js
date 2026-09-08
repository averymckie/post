// Independent-runtime oracle: builds an event log from a CSV file with pm4js 0.0.38 under node and
// prints the frequency directly-follows graph the library discovers, as one JSON object with the
// path frequencies, the start activities and the end activities.
// Usage: node dfg_oracle.js <log.csv> <case column> <activity column> <timestamp column>
require('pm4js');
const fs = require('fs');
const log = CsvImporter.apply(fs.readFileSync(process.argv[2], 'utf-8'), ',', '"',
                              process.argv[3], process.argv[4], process.argv[5]);
const dfg = FrequencyDfgDiscovery.apply(log);
process.stdout.write(JSON.stringify({paths: dfg.pathsFrequency,
                                     start: dfg.startActivities,
                                     end: dfg.endActivities}));
