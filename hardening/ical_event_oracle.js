// Independent-runtime oracle: parses one iCalendar file with ical.js 2.2.1 under node and prints one
// tab-separated line per VEVENT -- the UID as hex, the SUMMARY as hex, whether the start is a date
// rather than a date-time, the start as that library renders it, whether a LOCATION and an ATTENDEE
// are present, and the number of VALARM subcomponents.
// Usage: NODE_PATH=<prefix>/node_modules node ical_event_oracle.js <calendar.ics>
const fs = require('fs');
const loaded = require('ical.js');
const ICAL = loaded.default || loaded;
const root = new ICAL.Component(ICAL.parse(fs.readFileSync(process.argv[2], 'utf8')));
for (const component of root.getAllSubcomponents('vevent')) {
  const event = new ICAL.Event(component);
  console.log([
    Buffer.from(event.uid, 'utf8').toString('hex'),
    Buffer.from(event.summary, 'utf8').toString('hex'),
    String(event.startDate.isDate),
    event.startDate.toString(),
    String(component.getFirstPropertyValue('location') !== null),
    String(component.getFirstPropertyValue('attendee') !== null),
    String(component.getAllSubcomponents('valarm').length)
  ].join('\t'));
}
