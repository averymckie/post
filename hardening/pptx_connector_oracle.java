// Independent-runtime oracle: reads one .pptx with Apache POI 5.4.1 under Java and prints one
// tab-separated line per shape and per bound connector end. Shape lines carry the shape id, the
// shape name and the anchor rectangle in points; ST and END lines carry the connector's own shape
// id, the shape id the end is bound to and the connection point index stored with it.
// Usage: java -Dlog4j2.statusLoggerLevel=OFF -cp "<poi jars>/*" pptx_connector_oracle.java <deck.pptx>
import java.io.FileInputStream;
import java.awt.geom.Rectangle2D;
import org.apache.poi.xslf.usermodel.XMLSlideShow;
import org.apache.poi.xslf.usermodel.XSLFShape;
import org.apache.poi.xslf.usermodel.XSLFSlide;
import org.apache.poi.xslf.usermodel.XSLFConnectorShape;
import org.openxmlformats.schemas.presentationml.x2006.main.CTConnector;
import org.openxmlformats.schemas.drawingml.x2006.main.CTNonVisualConnectorProperties;

public class PptxConnectorOracle {
    public static void main(String[] args) throws Exception {
        XMLSlideShow show = new XMLSlideShow(new FileInputStream(args[0]));
        for (XSLFSlide slide : show.getSlides()) {
            for (XSLFShape shape : slide.getShapes()) {
                Rectangle2D box = shape.getAnchor();
                System.out.println("SHAPE\t" + shape.getShapeId() + "\t" + shape.getShapeName() + "\t"
                        + box.getX() + "\t" + box.getY() + "\t" + box.getWidth() + "\t" + box.getHeight());
            }
            for (XSLFShape shape : slide.getShapes()) {
                if (shape instanceof XSLFConnectorShape) {
                    CTNonVisualConnectorProperties properties =
                            ((CTConnector) shape.getXmlObject()).getNvCxnSpPr().getCNvCxnSpPr();
                    if (properties.isSetStCxn()) {
                        System.out.println("ST\t" + shape.getShapeId() + "\t" + properties.getStCxn().getId()
                                + "\t" + properties.getStCxn().getIdx());
                    }
                    if (properties.isSetEndCxn()) {
                        System.out.println("END\t" + shape.getShapeId() + "\t" + properties.getEndCxn().getId()
                                + "\t" + properties.getEndCxn().getIdx());
                    }
                }
            }
        }
        show.close();
    }
}
