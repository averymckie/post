// Independent-runtime oracle: reads one .xlsx with Apache POI 5.4.1 under Java and prints one
// tab-separated line per cell of one column, for each of the three policies POI's
// Row.MissingCellPolicy names. Each line carries the policy name, the zero-based row number, the
// cell type POI reports (or MISSING when the accessor returns null), the formula string when the
// cell holds one, and the cached value POI reads back. Nothing here computes: the branch is on the
// cell's type, which decides which accessor of the library to call, and the printed values come
// straight from those accessors. POI numbers rows and columns from zero, where openpyxl numbers
// both from one and addresses a column by letter; the Python side does that translation, not this
// shim.
// Usage: java -Dlog4j2.statusLoggerLevel=OFF -cp "<poi jars>/*" excel_cell_oracle.java <book.xlsx> <column>
import java.io.FileInputStream;
import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.CellType;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

public class ExcelCellOracle {
    static String describe(Cell cell) {
        if (cell == null) {
            return "MISSING\t\t";
        }
        CellType type = cell.getCellType();
        if (type == CellType.FORMULA) {
            return "FORMULA\t" + cell.getCellFormula() + "\t" + cell.getNumericCellValue();
        }
        if (type == CellType.NUMERIC) {
            return "NUMERIC\t\t" + cell.getNumericCellValue();
        }
        if (type == CellType.STRING) {
            return "STRING\t\t" + cell.getStringCellValue();
        }
        return type.name() + "\t\t";
    }

    public static void main(String[] args) throws Exception {
        XSSFWorkbook book = new XSSFWorkbook(new FileInputStream(args[0]));
        int column = Integer.parseInt(args[1]);
        Sheet sheet = book.getSheetAt(0);
        for (Row.MissingCellPolicy policy : Row.MissingCellPolicy.values()) {
            for (int number = 0; number <= sheet.getLastRowNum(); number++) {
                Row row = sheet.getRow(number);
                Cell cell = row == null ? null : row.getCell(column, policy);
                System.out.println(policy.name() + "\t" + number + "\t" + describe(cell));
            }
        }
        book.close();
    }
}
