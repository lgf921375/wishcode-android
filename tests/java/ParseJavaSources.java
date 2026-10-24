import javax.tools.*;
import com.sun.source.util.JavacTask;
/** 仅解析语法，不伪装 Android 类型检查或构建。 */
public class ParseJavaSources {
  public static void main(String[] args) throws Exception {
    var compiler = ToolProvider.getSystemJavaCompiler();
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    try (var manager = compiler.getStandardFileManager(diagnostics, null, null)) {
      var files = manager.getJavaFileObjectsFromStrings(java.util.Arrays.asList(args));
      var task = (JavacTask) compiler.getTask(null, manager, diagnostics,
          java.util.List.of("-proc:none"), null, files);
      task.parse();
      for (var diagnostic : diagnostics.getDiagnostics())
        if (diagnostic.getKind() == Diagnostic.Kind.ERROR) throw new AssertionError(diagnostic);
      System.out.println("Java syntax parsed: " + args.length + " files; Android types NOT checked");
    }
  }
}
