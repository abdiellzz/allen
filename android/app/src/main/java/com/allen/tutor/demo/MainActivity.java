package com.allen.tutor.demo;

import android.app.Activity;
import android.Manifest;
import android.content.pm.PackageManager;
import android.webkit.JavascriptInterface;
import org.json.JSONObject;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.graphics.Insets;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.WindowInsets;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;

import androidx.webkit.WebViewAssetLoader;

/**
 * ALLEN Android: a WebView serving bundled lessons and a prepared tutor from APK assets.
 * Learning, profiles and progress work locally without a Python runtime or Internet.
 */
public class MainActivity extends Activity {
    private static final String HOST = "appassets.androidplatform.net";
    private static final int FILE_REQUEST = 1;
    private static final int EXPORT_REQUEST = 2;
    private String pendingBackup;
    static volatile boolean foreground;

    private WebView webView;
    private boolean closingShown;
    private int reminderHour = 18, reminderMinute = 0;
    private ValueCallback<Uri[]> fileCallback;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if ((getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE) != 0) {
            WebView.setWebContentsDebuggingEnabled(true);
        }

        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(getColor(R.color.allen_cream));
        webView = new WebView(this);
        root.addView(webView);
        setContentView(root);
        applySystemBarPadding(root);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        webView.addJavascriptInterface(new ReminderBridge(), "AllenReminders");
        webView.addJavascriptInterface(new BackupBridge(), "AllenFiles");
        LearningReminder.createChannel(this);

        WebViewAssetLoader assetLoader = new WebViewAssetLoader.Builder()
                .setDomain(HOST)
                .addPathHandler("/", new AppAssets(new WebViewAssetLoader.AssetsPathHandler(this)))
                .build();

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                return assetLoader.shouldInterceptRequest(request.getUrl());
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri url = request.getUrl();
                if ("https".equals(url.getScheme()) && HOST.equals(url.getHost())) {
                    return false;
                }
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, url));
                } catch (ActivityNotFoundException ignored) {
                    // No app can open this link; stay in ALLEN.
                }
                return true;
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
                if (fileCallback != null) {
                    fileCallback.onReceiveValue(null);
                }
                fileCallback = callback;
                // Use Android's document picker; no broad storage permission is required.
                Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.setType(java.util.Arrays.asList(params.getAcceptTypes()).contains("application/json") ? "application/json" : "*/*");
                try {
                    startActivityForResult(Intent.createChooser(intent, "Selecciona un archivo"), FILE_REQUEST);
                } catch (ActivityNotFoundException e) {
                    fileCallback = null;
                    return false;
                }
                return true;
            }
        });

        if (savedInstanceState == null) {
            webView.loadUrl("https://" + HOST + "/mobile/index.html");
        } else {
            webView.restoreState(savedInstanceState);
        }
    }

    private boolean trustedPage() {
        String url = webView.getUrl();
        return url != null && url.startsWith("https://" + HOST + "/mobile/");
    }
    private void reportFile(String message) {
        if (trustedPage()) webView.evaluateJavascript("window.dispatchEvent(new CustomEvent('allen-file-status',{detail:"
                + JSONObject.quote(message) + "}))", null);
    }
    public final class BackupBridge {
        @JavascriptInterface public void exportProgress(String data) {
            runOnUiThread(() -> {
                if (!trustedPage() || data == null || data.length() > 2000000 || data.getBytes(java.nio.charset.StandardCharsets.UTF_8).length > 2000000 || pendingBackup != null) return;
                try {
                    JSONObject value = new JSONObject(data);
                    if (!"allen-mobile-backup".equals(value.optString("format")) || value.optInt("version") != 1) {
                        reportFile("La copia no es compatible."); return;
                    }
                    pendingBackup = data;
                    Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
                    intent.addCategory(Intent.CATEGORY_OPENABLE);
                    intent.setType("application/json");
                    intent.putExtra(Intent.EXTRA_TITLE, "allen-progreso.json");
                    startActivityForResult(intent, EXPORT_REQUEST);
                } catch (Exception error) {
                    pendingBackup = null;
                    reportFile("No se pudo abrir el selector de archivos. Tu progreso sigue guardado.");
                }
            });
        }
    }
    private void reportReminder(String message) {
        if (trustedPage()) webView.evaluateJavascript("window.dispatchEvent(new CustomEvent('allen-reminder-status',{detail:"
                + JSONObject.quote(message) + "}))", null);
    }
    private void enableReminder() {
        if (!LearningReminder.allowed(this)) {
            LearningReminder.preferences(this).edit().putBoolean("enabled", false).apply();
            LearningReminder.cancel(this);
            reportReminder("Android no permite las notificaciones de ALLEN. Puedes habilitarlas en los ajustes del teléfono.");
            return;
        }
        LearningReminder.preferences(this).edit().putBoolean("enabled", true)
                .putInt("hour", reminderHour).putInt("minute", reminderMinute).apply();
        LearningReminder.schedule(this);
        reportReminder(String.format(java.util.Locale.ROOT, "Recordatorio diario activado, alrededor de las %02d:%02d.", reminderHour, reminderMinute));
    }
    public final class ReminderBridge {
        @JavascriptInterface public void enable(int hour, int minute) {
            runOnUiThread(() -> {
                if (!trustedPage() || hour < 0 || hour > 23 || minute < 0 || minute > 59) return;
                reminderHour = hour; reminderMinute = minute;
                if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                        != PackageManager.PERMISSION_GRANTED) {
                    requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 33);
                } else enableReminder();
            });
        }
        @JavascriptInterface public void disable() {
            runOnUiThread(() -> {
                if (!trustedPage()) return;
                LearningReminder.preferences(MainActivity.this).edit().putBoolean("enabled", false).remove("summary").apply();
                LearningReminder.cancel(MainActivity.this);
                reportReminder("Recordatorios desactivados.");
            });
        }
        @JavascriptInterface public void saveSummary(String summary) {
            runOnUiThread(() -> {
                if (!trustedPage() || !LearningReminder.preferences(MainActivity.this).getBoolean("enabled", false)) return;
                String bounded = summary == null ? "" : summary.replaceAll("[\\p{Cntrl}]", " ");
                if (bounded.length() > 450) bounded = bounded.substring(0, 450);
                LearningReminder.preferences(MainActivity.this).edit().putString("summary", bounded).apply();
            });
        }
        @JavascriptInterface public void clearSummary() {
            runOnUiThread(() -> { if (trustedPage()) LearningReminder.preferences(MainActivity.this).edit().remove("summary").apply(); });
        }
        @JavascriptInterface public String status() {
            boolean enabled = LearningReminder.preferences(MainActivity.this).getBoolean("enabled", false);
            return enabled && LearningReminder.allowed(MainActivity.this) ? "Recordatorios diarios activados." : "Recordatorios desactivados o bloqueados por Android.";
        }
    }
    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {
        super.onRequestPermissionsResult(requestCode, permissions, results);
        if (requestCode == 33) {
            if (results.length > 0 && results[0] == PackageManager.PERMISSION_GRANTED) enableReminder();
            else {
                LearningReminder.preferences(this).edit().putBoolean("enabled", false).apply();
                LearningReminder.cancel(this);
                reportReminder("Permiso rechazado. Puedes seguir aprendiendo y activar los recordatorios más adelante.");
            }
        }
    }
    @Override protected void onStart() {
        super.onStart();
        foreground = true;
        LearningReminder.schedule(this);
        closingShown = false;
    }
    @Override protected void onStop() {
        if (trustedPage()) webView.evaluateJavascript("window.dispatchEvent(new Event('allen-background'))", null);
        foreground = false;
        super.onStop();
    }

    private void applySystemBarPadding(FrameLayout root) {
        // Android 15 draws apps edge-to-edge; keep ALLEN clear of the status bar and keyboard.
        root.setOnApplyWindowInsetsListener((view, insets) -> {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                Insets bars = insets.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.ime());
                view.setPadding(bars.left, bars.top, bars.right, bars.bottom);
            } else {
                view.setPadding(insets.getSystemWindowInsetLeft(), insets.getSystemWindowInsetTop(),
                        insets.getSystemWindowInsetRight(), insets.getSystemWindowInsetBottom());
            }
            return insets;
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == EXPORT_REQUEST) {
            String backup = pendingBackup;
            pendingBackup = null;
            Uri target = data == null ? null : data.getData();
            if (resultCode != RESULT_OK || target == null || backup == null) {
                reportFile("Guardado cancelado. Tu progreso sigue en ALLEN.");
            } else {
                new Thread(() -> {
                    String message;
                    try (java.io.OutputStream out = getContentResolver().openOutputStream(target, "wt")) {
                        if (out == null) throw new java.io.IOException("No output stream");
                        out.write(backup.getBytes(java.nio.charset.StandardCharsets.UTF_8));
                        message = "Copia guardada. Consérvala en un lugar privado; no está cifrada.";
                    } catch (Exception error) {
                        message = "No se pudo guardar el archivo. Tu progreso sigue en ALLEN; inténtalo otra vez.";
                    }
                    String result = message;
                    runOnUiThread(() -> {if (!isFinishing() && !isDestroyed()) reportFile(result);});
                }, "allen-backup-export").start();
            }
            return;
        }
        if (requestCode == FILE_REQUEST && fileCallback != null) {
            fileCallback.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(resultCode, data));
            fileCallback = null;
            return;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        webView.saveState(outState);
    }

    @Override
    public void onBackPressed() {
        if (trustedPage()) {
            webView.evaluateJavascript("Boolean(window.allenNavigateBack && window.allenNavigateBack())", handled -> {
                if ("true".equals(handled)) { closingShown = false; return; }
                if (!closingShown) {
                    closingShown = true;
                    webView.evaluateJavascript("window.dispatchEvent(new Event('allen-close-request'))", null);
                } else finish();
            });
        } else if (webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }

    @Override
    protected void onDestroy() {
        webView.destroy();
        super.onDestroy();
    }

    /** Maps the app's routes ("/", "/fair") to HTML files and everything else to assets/www. */
    private static final class AppAssets implements WebViewAssetLoader.PathHandler {
        private final WebViewAssetLoader.AssetsPathHandler assets;

        AppAssets(WebViewAssetLoader.AssetsPathHandler assets) {
            this.assets = assets;
        }

        @Override
        public WebResourceResponse handle(String path) {
            boolean studentEntry = path.isEmpty() || path.equals("index.html") ||
                    path.equals("fair") || path.equals("fair.html") ||
                    path.equals("static/index.html") || path.equals("static/fair.html") ||
                    path.equals("mobile/");
            String file = studentEntry ? "mobile/index.html" : path;
            WebResourceResponse response = assets.handle("www/" + file);
            if (response != null && file.endsWith(".wasm")) {
                // WebAssembly.instantiateStreaming requires this exact MIME type.
                response.setMimeType("application/wasm");
            }
            return response;
        }
    }
}
