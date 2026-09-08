// Independent-runtime oracle: builds pairs of ranges over the same ordered points with Guava
// 33.7.1-jre under Java and prints, for each pair, whether Guava calls the two ranges connected and
// whether their intersection is non-empty, one value per line. Bounds are integers; each closure is
// named with pandas' own vocabulary and mapped to the matching Range factory. Arguments come in
// groups of six, so one process answers every pair of one example.
// Usage: java -cp "<guava jars>/*" interval_overlap_oracle.java <a1> <b1> <closed1> <a2> <b2> <closed2> ...
import com.google.common.collect.Range;

public class IntervalOverlapOracle {
    static Range<Long> range(String start, String finish, String closed) {
        long left = Long.parseLong(start);
        long right = Long.parseLong(finish);
        switch (closed) {
            case "both": return Range.closed(left, right);
            case "left": return Range.closedOpen(left, right);
            case "right": return Range.openClosed(left, right);
            case "neither": return Range.open(left, right);
            default: throw new IllegalArgumentException(closed);
        }
    }

    public static void main(String[] args) {
        for (int at = 0; at < args.length; at += 6) {
            Range<Long> first = range(args[at], args[at + 1], args[at + 2]);
            Range<Long> second = range(args[at + 3], args[at + 4], args[at + 5]);
            System.out.println(first.isConnected(second));
            System.out.println(first.isConnected(second) && !first.intersection(second).isEmpty());
        }
    }
}
