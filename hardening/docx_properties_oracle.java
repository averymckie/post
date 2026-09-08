// Independent-runtime oracle: reads one .docx with Apache POI 5.4.1 under Java and prints the
// extended package properties it exposes, one tab-separated line each, followed by the number of body
// paragraphs POI itself counts in the document. Nothing here computes a page count or a word count:
// the property lines are the values POIXMLProperties.ExtendedProperties returns, and the paragraph
// line is the size of the list XWPFDocument.getParagraphs() returns.
// Usage: java -Dlog4j2.statusLoggerLevel=OFF -cp "<poi jars>/*" docx_properties_oracle.java <file.docx>
import java.io.FileInputStream;
import org.apache.poi.ooxml.POIXMLProperties;
import org.apache.poi.xwpf.usermodel.XWPFDocument;

public class DocxPropertiesOracle {
    public static void main(String[] args) throws Exception {
        XWPFDocument document = new XWPFDocument(new FileInputStream(args[0]));
        POIXMLProperties.ExtendedProperties extended = document.getProperties().getExtendedProperties();
        System.out.println("PAGES\t" + extended.getPages());
        System.out.println("WORDS\t" + extended.getWords());
        System.out.println("CHARACTERS\t" + extended.getCharacters());
        System.out.println("APPLICATION\t" + extended.getApplication());
        System.out.println("COUNTED_PARAGRAPHS\t" + document.getParagraphs().size());
        document.close();
    }
}
