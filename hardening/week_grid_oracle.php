<?php
// Independent-runtime oracle: lays out a month with ICU's calendar through PHP's intl extension and
// prints, for each day of that month, the week of the month and the day of the week ICU assigns it.
// Arguments come in groups of four -- year, month, first weekday, minimal days in the first week -- so
// one process answers every month of one example. Two translations of vocabulary and nothing else: the
// month arrives numbered from one as CPython's calendar module numbers it and ICU numbers its months
// from zero, and the first weekday arrives numbered Monday 0 through Sunday 6 as that module numbers it
// while ICU numbers the same seven days Sunday 1 through Saturday 7. Each group prints one line: the
// length of the month, then one tab-separated field per day holding the week of the month and the day
// of the week separated by a comma.
// Usage: php week_grid_oracle.php <year> <month> <first-weekday> <minimal-days> ...
$arguments = array_slice($argv, 1);
for ($at = 0; $at < count($arguments); $at += 4) {
    $year = (int) $arguments[$at];
    $month = (int) $arguments[$at + 1] - 1;
    $calendar = IntlCalendar::createInstance(new DateTimeZone('UTC'), 'en_US');
    $calendar->setFirstDayOfWeek(((int) $arguments[$at + 2] + 1) % 7 + 1);
    $calendar->setMinimalDaysInFirstWeek((int) $arguments[$at + 3]);
    $calendar->setTime(0);
    $calendar->set($year, $month, 1);
    $length = $calendar->getActualMaximum(IntlCalendar::FIELD_DAY_OF_MONTH);
    $line = (string) $length;
    for ($day = 1; $day <= $length; $day++) {
        $calendar->set($year, $month, $day);
        $line .= "\t" . $calendar->get(IntlCalendar::FIELD_WEEK_OF_MONTH);
        $line .= "," . $calendar->get(IntlCalendar::FIELD_DAY_OF_WEEK);
    }
    echo $line . "\n";
}
