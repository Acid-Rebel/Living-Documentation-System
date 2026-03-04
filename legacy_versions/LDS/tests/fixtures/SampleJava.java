package fixtures;

import java.util.List;

public class SampleJava {
    private final String name;

    public SampleJava(String name) {
        this.name = name;
    }

    public int sum(List<Integer> values) {
        int total = 0;
        for (Integer value : values) {
            total += value;
        }
        return total;
    }
}
