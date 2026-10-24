package com.deepseekharness.app.util;

import java.net.URI;

/** 开发预览仅接受显式端口；不做 DNS 查询，不接受凭据或鉴权查询串。 */
public final class WishCodePreviewPolicy {
  private WishCodePreviewPolicy() {}

  public static String normalize(String value, int chatPort) {
    try {
      if (value == null || value.length() > 2048 || !value.equals(value.trim())) return null;
      URI uri = new URI(value);
      String host = uri.getHost();
      int port = uri.getPort();
      if (!"http".equals(uri.getScheme())
          || !("127.0.0.1".equals(host) || "localhost".equals(host))
          || uri.getRawUserInfo() != null || port < 1024 || port > 65535
          || port == chatPort || port == 3081 || port == 3090
          || uri.getRawQuery() != null || uri.getRawFragment() != null
          || value.indexOf('\\') >= 0) return null;
      String path = uri.getRawPath();
      return "http://127.0.0.1:" + port + (path == null || path.isEmpty() ? "/" : path);
    } catch (Exception invalid) {
      return null;
    }
  }

  public static int port(String value) {
    try { return new URI(value).getPort(); }
    catch (Exception invalid) { return -1; }
  }

  public static boolean sameOrigin(String approved, String candidate) {
    try {
      URI base = new URI(approved), uri = new URI(candidate);
      return "http".equals(uri.getScheme()) && "127.0.0.1".equals(uri.getHost())
          && uri.getPort() == base.getPort() && uri.getRawUserInfo() == null
          && candidate.indexOf('\\') < 0;
    } catch (Exception invalid) { return false; }
  }

  public static String csp(String approved) {
    String origin = "http://127.0.0.1:" + port(approved);
    return "default-src 'none'; script-src " + origin + " 'unsafe-inline'; "
        + "style-src " + origin + " 'unsafe-inline'; img-src " + origin + " data:; "
        + "font-src " + origin + "; media-src " + origin + "; connect-src " + origin
        + "; form-action 'none'; frame-src 'none'; object-src 'none'; worker-src 'none'; base-uri 'none'";
  }
}
