// Independent-runtime oracle: lays out a month with java.time.temporal.WeekFields under OpenJDK 21 and
// prints, for each day of that month, the week of the month and the day of the week that WeekFields
// assigns it. Arguments come in groups of four -- year, month, first weekday, minimal days in the first
// week -- so one process answers every month of one example. The only translation is of vocabulary: the
// first weekday arrives numbered as CPython's calendar module numbers it, Monday 0 through Sunday 6,
// and java.time.DayOfWeek numbers the same seven days Monday 1 through Sunday 7, so DayOfWeek.of takes
// the neighbouring value. Each group prints one line: the length of the month, then one tab-separated
// field per day holding the week of the month and the day of the week separated by a comma.
// Usage: java week_grid_oracle.java <year> <month> <first-weekday> <minimal-days> ...
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.YearMonth;
import java.time.temporal.WeekFields;

public class WeekGridOracle {
    public static void main(String[] args) {
        for (int at = 0; at < args.length; at += 4) {
            int year = Integer.parseInt(args[at]);
            int month = Integer.parseInt(args[at + 1]);
            WeekFields fields = WeekFields.of(DayOfWeek.of(Integer.parseInt(args[at + 2]) + 1),
                                              Integer.parseInt(args[at + 3]));
            int length = YearMonth.of(year, month).lengthOfMonth();
            StringBuilder line = new StringBuilder(Integer.toString(length));
            for (int day = 1; day <= length; day++) {
                LocalDate date = LocalDate.of(year, month, day);
                line.append('\t').append(date.get(fields.weekOfMonth()));
                line.append(',').append(date.get(fields.dayOfWeek()));
            }
            System.out.println(line);
        }
    }
}
