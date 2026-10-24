import com.deepseekharness.app.util.WishCodePreviewPolicy;
import com.deepseekharness.app.util.WishCodePreviewHttp;
import com.sun.net.httpserver.HttpServer;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.atomic.AtomicInteger;

public final class WishCodePreviewTest {
  private static int count;
  private static void check(boolean value, String name) {
    if (!value) throw new AssertionError(name);
    count++; System.out.println("PASS " + name);
  }
  public static void main(String[] args) throws Exception {
    String canonical = "http://127.0.0.1:4181/";
    check(canonical.equals(WishCodePreviewPolicy.normalize("http://localhost:4181", 5555)), "localhost normalization");
    check(canonical.equals(WishCodePreviewPolicy.normalize(canonical, 5555)), "explicit IPv4 port");
    check("http://127.0.0.1:65535/a%20b.html".equals(WishCodePreviewPolicy.normalize("http://localhost:65535/a%20b.html", 5555)), "encoded path preserved");
    String[] rejected = {"https://127.0.0.1:4181/", "http://127.0.0.1/", "http://127.0.0.1:0/", "http://127.0.0.1:65536/", "http://127.0.0.1:80/", "http://127.0.0.1:3081/", "http://127.0.0.1:3090/", "http://127.0.0.1:5555/", "http://user:pass@127.0.0.1:4181/", "http://127.0.0.1:4181/?token=secret", "http://127.0.0.1:4181/#secret", "http://localhost.evil:4181/", "http://127.1:4181/", "http://2130706433:4181/", "http://0.0.0.0:4181/", "http://192.168.1.1:4181/", "http://[::1]:4181/", "file:///data/data/", "content://data", "javascript:alert(1)", "intent://host", " http://127.0.0.1:4181/", "http://127.0.0.1:4181/\\evil", "http://127.0.0.1:4181/\n", null};
    for (int i = 0; i < rejected.length; i++) check(WishCodePreviewPolicy.normalize(rejected[i], 5555) == null, "reject URL case " + i);
    check(WishCodePreviewPolicy.sameOrigin(canonical, canonical + "x?q=1"), "same-origin resource query");
    check(!WishCodePreviewPolicy.sameOrigin(canonical, "http://127.0.0.1:5555/"), "cross-port resource denied");
    check(!WishCodePreviewPolicy.sameOrigin(canonical, "http://evil:4181/"), "external resource denied");
    check(!WishCodePreviewPolicy.sameOrigin(canonical, "http://secret@127.0.0.1:4181/"), "resource credentials denied");
    check(!WishCodePreviewPolicy.sameOrigin(null, canonical), "missing approval denied");
    check(WishCodePreviewPolicy.csp(canonical).contains("worker-src 'none'"), "workers denied");
    check(WishCodePreviewPolicy.csp(canonical).contains("connect-src http://127.0.0.1:4181;"), "connect restricted");
    HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
    AtomicInteger leakedHeaders = new AtomicInteger(), redirected = new AtomicInteger();
    server.createContext("/", exchange -> {
      if (exchange.getRequestHeaders().containsKey("Cookie") || exchange.getRequestHeaders().containsKey("Authorization")) leakedHeaders.incrementAndGet();
      String path = exchange.getRequestURI().getPath();
      if (path.equals("/target")) redirected.incrementAndGet();
      if (path.equals("/redirect")) { exchange.getResponseHeaders().add("Location", "/target"); exchange.sendResponseHeaders(302, -1); exchange.close(); return; }
      int code = path.equals("/missing") ? 404 : 200;
      byte[] body = (code == 200 ? "<h1>中文预览</h1>" : "missing").getBytes(StandardCharsets.UTF_8);
      exchange.getResponseHeaders().add("Content-Type", "text/html; charset=UTF-8");
      exchange.getResponseHeaders().add("Set-Cookie", "secret=never-forward");
      exchange.sendResponseHeaders(code, body.length); exchange.getResponseBody().write(body); exchange.close();
    });
    server.start();
    String base = "http://127.0.0.1:" + server.getAddress().getPort() + "/";
    try {
      try (var response = WishCodePreviewHttp.get(base, base, "GET")) {
        check(response.code == 200, "real HTTP 200");
        check("text/html".equals(response.mime), "HTML MIME");
        check(new String(response.body.readAllBytes(), StandardCharsets.UTF_8).contains("中文预览"), "UTF-8 response body");
      }
      try (var response = WishCodePreviewHttp.get(base, base + "missing", "GET")) {
        check(response.code == 404, "real HTTP 404 preserved");
      }
      try { WishCodePreviewHttp.get(base, base + "redirect", "GET"); throw new AssertionError("redirect accepted"); }
      catch (java.io.IOException expected) { check(expected.getMessage().startsWith("PREVIEW_REDIRECT_BLOCKED"), "redirect rejected"); }
      check(redirected.get() == 0, "redirect target never requested");
      try { WishCodePreviewHttp.get(base, base, "POST"); throw new AssertionError("POST accepted"); }
      catch (java.io.IOException expected) { check(true, "POST rejected before network"); }
      try { WishCodePreviewHttp.get(base, "http://127.0.0.1:3090/", "GET"); throw new AssertionError("bridge accepted"); }
      catch (java.io.IOException expected) { check(true, "cross-port rejected before network"); }
      check(leakedHeaders.get() == 0, "no Cookie or Authorization sent");
    } finally { server.stop(0); }
    try { WishCodePreviewHttp.get(base, base, "GET"); throw new AssertionError("stopped server succeeded"); }
    catch (java.io.IOException expected) { check(true, "stopped server is connection error"); }
    System.out.println("TOTAL " + count + " passed; Android WebView/device NOT tested");
  }
}
