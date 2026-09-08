// Independent-runtime oracle: reads one ZIP archive with the java.util.zip implementation in the
// OpenJDK class library and prints one tab-separated line per entry -- the entry name as hex, the
// six components of the entry's MS-DOS local date-time, the storage method, the uncompressed size
// and the CRC-32 the archive carries -- then writes a second archive holding the same entries,
// stored, under the same names, in the same order and with the same local date-times.
// Usage: java zip_package_oracle.java <archive.zip> <archive-written-by-java.zip>
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.HexFormat;
import java.util.zip.CRC32;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.zip.ZipOutputStream;

public class ZipPackageOracle {
    public static void main(String[] args) throws Exception {
        ByteArrayOutputStream written = new ByteArrayOutputStream();
        try (ZipFile archive = new ZipFile(args[0]);
             ZipOutputStream out = new ZipOutputStream(written)) {
            var entries = archive.entries();
            while (entries.hasMoreElements()) {
                ZipEntry entry = entries.nextElement();
                byte[] data = archive.getInputStream(entry).readAllBytes();
                LocalDateTime stamp = entry.getTimeLocal();
                System.out.println(
                        HexFormat.of().formatHex(entry.getName().getBytes(StandardCharsets.UTF_8))
                        + "\t" + stamp.getYear() + "\t" + stamp.getMonthValue()
                        + "\t" + stamp.getDayOfMonth() + "\t" + stamp.getHour()
                        + "\t" + stamp.getMinute() + "\t" + stamp.getSecond()
                        + "\t" + entry.getMethod() + "\t" + entry.getSize() + "\t" + entry.getCrc());
                ZipEntry copy = new ZipEntry(entry.getName());
                copy.setMethod(ZipEntry.STORED);
                copy.setSize(data.length);
                copy.setCompressedSize(data.length);
                CRC32 crc = new CRC32();
                crc.update(data);
                copy.setCrc(crc.getValue());
                copy.setTimeLocal(stamp);
                out.putNextEntry(copy);
                out.write(data);
                out.closeEntry();
            }
        }
        Files.write(Path.of(args[1]), written.toByteArray());
    }
}
