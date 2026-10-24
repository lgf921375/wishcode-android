package com.deepseekharness.app.util;

import java.io.*;
import java.net.*;

/** 预览的 GET 传输；禁止代理、重定向、Cookie 和请求头透传。 */
public final class WishCodePreviewHttp {
  private WishCodePreviewHttp() {}

  public static final class Response implements AutoCloseable {
    public final int code;
    public final String mime, encoding;
    public final InputStream body;
    Response(int code, String mime, String encoding, InputStream body) {
      this.code = code; this.mime = mime; this.encoding = encoding; this.body = body;
    }
    @Override public void close() throws IOException { body.close(); }
  }

  public static Response get(String approved, String url, String method) throws IOException {
    if (!WishCodePreviewPolicy.sameOrigin(approved, url) || !"GET".equals(method))
      throw new IOException("PREVIEW_REQUEST_BLOCKED");
    HttpURLConnection connection = (HttpURLConnection) new URL(url).openConnection(Proxy.NO_PROXY);
    try {
      connection.setInstanceFollowRedirects(false);
      connection.setConnectTimeout(4000);
      connection.setReadTimeout(5000);
      connection.setUseCaches(false);
      connection.setRequestProperty("Accept-Encoding", "identity");
      int code = connection.getResponseCode();
      // WebResourceResponse 不能返回重定向；由用户重新确认最终地址。
      if (code >= 300 && code < 400) throw new IOException("PREVIEW_REDIRECT_BLOCKED_HTTP_" + code);
      String type = connection.getContentType();
      String mime = type == null ? "application/octet-stream" : type.split(";", 2)[0].trim();
      String encoding = "UTF-8";
      if (type != null) for (String part : type.split(";"))
        if (part.trim().toLowerCase(java.util.Locale.ROOT).startsWith("charset="))
          encoding = part.trim().substring(8).replace("\"", "");
      InputStream body = code >= 400 ? connection.getErrorStream() : connection.getInputStream();
      if (body == null) body = new ByteArrayInputStream(new byte[0]);
      InputStream stream = new FilterInputStream(body) {
        @Override public void close() throws IOException {
          try { super.close(); } finally { connection.disconnect(); }
        }
      };
      return new Response(code, mime, encoding, stream);
    } catch (IOException | RuntimeException error) {
      connection.disconnect(); throw error;
    }
  }
}
