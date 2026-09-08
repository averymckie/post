// Independent-runtime oracle: reads one .docx with Apache POI 5.4.1 under Java and prints what the
// library reports about every table it finds, one tab-separated line at a time. For each row it prints
// the two row-property readings POI exposes, isRepeatHeader and isCantSplitRow, and whether XMLBeans
// validates the row element. For each cell it prints the single string XWPFTableCell.getText() returns,
// and then one line per paragraph inside that cell carrying XWPFParagraph.getText(). Nothing here
// computes and nothing branches on a value: the numbers are loop positions and every printed field is
// the return of one accessor.
// Usage: java -Dlog4j2.statusLoggerLevel=OFF -cp "<poi jars>/*" docx_table_oracle.java <file.docx>
import java.io.FileInputStream;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFParagraph;
import org.apache.poi.xwpf.usermodel.XWPFTable;
import org.apache.poi.xwpf.usermodel.XWPFTableCell;
import org.apache.poi.xwpf.usermodel.XWPFTableRow;

public class DocxTableOracle {
    public static void main(String[] args) throws Exception {
        XWPFDocument document = new XWPFDocument(new FileInputStream(args[0]));
        int tableNumber = 0;
        for (XWPFTable table : document.getTables()) {
            int rowNumber = 0;
            for (XWPFTableRow row : table.getRows()) {
                System.out.println("ROW\t" + tableNumber + "\t" + rowNumber + "\t"
                                   + row.isRepeatHeader() + "\t" + row.isCantSplitRow() + "\t"
                                   + row.getCtRow().validate());
                int cellNumber = 0;
                for (XWPFTableCell cell : row.getTableCells()) {
                    System.out.println("CELL\t" + tableNumber + "\t" + rowNumber + "\t"
                                       + cellNumber + "\t" + cell.getText());
                    int paragraphNumber = 0;
                    for (XWPFParagraph paragraph : cell.getParagraphs()) {
                        System.out.println("PARA\t" + tableNumber + "\t" + rowNumber + "\t"
                                           + cellNumber + "\t" + paragraphNumber + "\t"
                                           + paragraph.getText());
                        paragraphNumber++;
                    }
                    cellNumber++;
                }
                rowNumber++;
            }
            tableNumber++;
        }
        document.close();
    }
}
