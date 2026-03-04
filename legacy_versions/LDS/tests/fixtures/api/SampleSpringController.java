package fixtures.api;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class SampleSpringController {

    @GetMapping("/status")
    public String status() {
        return "ok";
    }

    @PostMapping(path = "/items")
    public String createItem() {
        return "created";
    }

    @RequestMapping(value = {"/fallback", "/legacy"}, method = RequestMethod.PUT)
    public String fallback() {
        return "fallback";
    }

    @PatchMapping(path = "/items/{id}")
    public String updateItem() {
        return "updated";
    }
}
