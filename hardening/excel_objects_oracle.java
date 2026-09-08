// Independent-runtime oracle: reads one .xlsx with Apache POI 5.4.1 under Java and prints the objects
// the first sheet carries besides its cells -- one tab-separated line per table, with the name and the
// area POI reports, formatted by AreaReference itself, and one per chart in the sheet's drawing, with the chart class POI instantiated.
// Nothing here computes; the numbers are loop positions, every other field is the return of one
// accessor, and the only branch is the null a sheet with no drawing returns.
// Usage: java -Dlog4j2.statusLoggerLevel=OFF -cp "<poi jars>/*" excel_objects_oracle.java <book.xlsx>
import java.io.FileInputStream;
import org.apache.poi.xssf.usermodel.XSSFChart;
import org.apache.poi.xssf.usermodel.XSSFDrawing;
import org.apache.poi.xssf.usermodel.XSSFSheet;
import org.apache.poi.xssf.usermodel.XSSFTable;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

public class ExcelObjectsOracle {
    public static void main(String[] args) throws Exception {
        XSSFWorkbook book = new XSSFWorkbook(new FileInputStream(args[0]));
        XSSFSheet sheet = book.getSheetAt(0);
        int tableNumber = 0;
        for (XSSFTable table : sheet.getTables()) {
            System.out.println("TABLE\t" + tableNumber + "\t" + table.getName() + "\t"
                               + table.getArea().formatAsString());
            tableNumber++;
        }
        XSSFDrawing drawing = sheet.getDrawingPatriarch();
        if (drawing != null) {
            int chartNumber = 0;
            for (XSSFChart chart : drawing.getCharts()) {
                System.out.println("CHART\t" + chartNumber + "\t"
                                   + chart.getClass().getSimpleName());
                chartNumber++;
            }
        }
        book.close();
    }
}
