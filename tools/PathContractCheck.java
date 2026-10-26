import androidx.core.graphics.PathParser;
import androidx.core.graphics.PathParser.PathDataNode;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;

/** Host-only check of the real cached AndroidX parser; never constructs a Path. */
public final class PathContractCheck {
    public static void main(String[] args) throws Exception {
        List<PathDataNode[]> nodes = new ArrayList<>();
        List<String> signatures = new ArrayList<>();
        int failures = 0;
        for (String line : Files.readAllLines(Path.of(args[0]), StandardCharsets.UTF_8)) {
            String[] fields = line.split("\t", -1);
            String data = new String(Base64.getDecoder().decode(fields[1]), StandardCharsets.UTF_8);
            PathDataNode[] parsed = PathParser.createNodesFromPathData(data);
            StringBuilder actual = new StringBuilder();
            for (PathDataNode node : parsed) {
                if (actual.length() > 0) actual.append(',');
                actual.append(node.getType()).append(node.getParams().length);
            }
            if (!actual.toString().equals(fields[2])) {
                System.out.println("SIGNATURE_MISMATCH " + fields[0] + " " + actual + " expected " + fields[2]);
                failures++;
            }
            nodes.add(parsed); signatures.add(fields[2]);
        }
        long pairs = 0;
        long morphable = 0;
        for (int i = 0; i < nodes.size(); i++) {
            for (int j = i; j < nodes.size(); j++) {
                boolean actual = PathParser.canMorph(nodes.get(i), nodes.get(j));
                boolean expected = signatures.get(i).equals(signatures.get(j));
                if (actual != expected) {
                    System.out.println("MORPH_MISMATCH " + i + " " + j);
                    failures++;
                }
                pairs++;
                if (actual) morphable++;
            }
        }
        System.out.println("{\"parsedPaths\":"+nodes.size()+",\"pairChecks\":"+pairs+
            ",\"morphablePairs\":"+morphable+",\"failures\":"+failures+"}");
        if (failures != 0) System.exit(1);
    }
}
