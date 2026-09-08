// Independent-runtime oracle: reads one .docx with Apache POI 5.4.1 under Java and prints what the
// library reports about the document's paragraphs and about every section-properties element it
// carries, one tab-separated line at a time. A PARA line carries the return of XWPFParagraph.getText()
// for each paragraph of XWPFDocument.getParagraphs(), in document order. A SECT line carries the page
// width POI reads out of one CTSectPr: first the sectPr elements that sit inside a paragraph's
// CTPPr, in document order, then the one CTBody.getSectPr() returns, which is the last section of the
// document. Nothing here computes and nothing branches on a value: the numbers are loop positions and
// every printed field is the return of one accessor, rendered with String.valueOf.
// Usage: java -Dlog4j2.statusLoggerLevel=OFF -cp "<poi jars>/*" docx_section_oracle.java <file.docx>
import java.io.FileInputStream;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFParagraph;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTSectPr;

public class DocxSectionOracle {
    private static void printSection(int number, CTSectPr properties) {
        System.out.println("SECT\t" + number + "\t"
                           + String.valueOf(properties.getPgSz().getW()) + "\t"
                           + String.valueOf(properties.getPgSz().getH()));
    }

    public static void main(String[] args) throws Exception {
        XWPFDocument document = new XWPFDocument(new FileInputStream(args[0]));
        int paragraphNumber = 0;
        int sectionNumber = 0;
        for (XWPFParagraph paragraph : document.getParagraphs()) {
            System.out.println("PARA\t" + paragraphNumber + "\t" + paragraph.getText());
            if (paragraph.getCTP().isSetPPr() && paragraph.getCTP().getPPr().isSetSectPr()) {
                printSection(sectionNumber, paragraph.getCTP().getPPr().getSectPr());
                sectionNumber++;
            }
            paragraphNumber++;
        }
        if (document.getDocument().getBody().isSetSectPr()) {
            printSection(sectionNumber, document.getDocument().getBody().getSectPr());
        }
        document.close();
    }
}
