// Independent-runtime oracle: reads one .pptx with Apache POI 5.4.1 under Java and prints one
// tab-separated line per top-level shape, per table cell, per chart series and per cached point.
// SHAPE lines carry the shape's ordinal and POI's own class name; TEXT lines the text of a text
// shape; TABLESIZE and CELL the table's dimensions and each cell's text; SERIES the point count
// and the range reference the cache was filled from; VALUE and CATEGORY each cached point.
// Usage: java -Dlog4j2.statusLoggerLevel=OFF -cp "<poi jars>/*" pptx_deck_oracle.java <deck.pptx>
import java.io.FileInputStream;
import org.apache.poi.xslf.usermodel.XMLSlideShow;
import org.apache.poi.xslf.usermodel.XSLFChart;
import org.apache.poi.xslf.usermodel.XSLFGraphicFrame;
import org.apache.poi.xslf.usermodel.XSLFShape;
import org.apache.poi.xslf.usermodel.XSLFSlide;
import org.apache.poi.xslf.usermodel.XSLFTable;
import org.apache.poi.xslf.usermodel.XSLFTextShape;
import org.apache.poi.xddf.usermodel.chart.XDDFChartData;
import org.apache.poi.xddf.usermodel.chart.XDDFDataSource;
import org.apache.poi.xddf.usermodel.chart.XDDFNumericalDataSource;

public class PptxDeckOracle {
    public static void main(String[] args) throws Exception {
        XMLSlideShow show = new XMLSlideShow(new FileInputStream(args[0]));
        for (XSLFSlide slide : show.getSlides()) {
            int index = 0;
            for (XSLFShape shape : slide.getShapes()) {
                System.out.println("SHAPE\t" + index + "\t" + shape.getClass().getSimpleName());
                if (shape instanceof XSLFTable) {
                    XSLFTable table = (XSLFTable) shape;
                    System.out.println("TABLESIZE\t" + index + "\t" + table.getNumberOfRows()
                            + "\t" + table.getNumberOfColumns());
                    for (int r = 0; r < table.getNumberOfRows(); r++) {
                        for (int c = 0; c < table.getNumberOfColumns(); c++) {
                            System.out.println("CELL\t" + index + "\t" + r + "\t" + c + "\t"
                                    + table.getCell(r, c).getText());
                        }
                    }
                } else if (shape instanceof XSLFTextShape) {
                    System.out.println("TEXT\t" + index + "\t" + ((XSLFTextShape) shape).getText());
                } else if (shape instanceof XSLFGraphicFrame && ((XSLFGraphicFrame) shape).hasChart()) {
                    XSLFChart chart = ((XSLFGraphicFrame) shape).getChart();
                    int number = 0;
                    for (XDDFChartData data : chart.getChartSeries()) {
                        for (XDDFChartData.Series series : data.getSeries()) {
                            XDDFNumericalDataSource<? extends Number> values = series.getValuesData();
                            XDDFDataSource<?> categories = series.getCategoryData();
                            System.out.println("SERIES\t" + index + "\t" + number + "\t"
                                    + values.getPointCount() + "\t" + values.getDataRangeReference());
                            for (int p = 0; p < values.getPointCount(); p++) {
                                System.out.println("VALUE\t" + index + "\t" + number + "\t" + p + "\t"
                                        + values.getPointAt(p));
                            }
                            for (int p = 0; p < categories.getPointCount(); p++) {
                                System.out.println("CATEGORY\t" + index + "\t" + number + "\t" + p + "\t"
                                        + categories.getPointAt(p));
                            }
                            number++;
                        }
                    }
                }
                index++;
            }
        }
        show.close();
    }
}
