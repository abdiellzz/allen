package com.allen.tutor.demo;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.graphics.Insets;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.WindowInsets;
import android.webkit.GeolocationPermissions;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;

import androidx.webkit.WebViewAssetLoader;

import java.io.ByteArrayInputStream;

/**
 * ALLEN Android demo: a WebView that serves the bundled mobile learning experience from APK
 * assets. Everything runs on the device; the app declares no permissions, not even Internet.
 */
public class MainActivity extends Activity {
    private static final String HOST = "appassets.androidplatform.net";
    private static final int FILE_REQUEST = 1;

    private WebView webView;
    private ValueCallback<Uri[]> fileCallback;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // Only local debug builds; published release builds are never debuggable.
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
        settings.setGeolocationEnabled(false);
        settings.setJavaScriptCanOpenWindowsAutomatically(false);
        settings.setSupportMultipleWindows(false);

        WebViewAssetLoader assetLoader = new WebViewAssetLoader.Builder()
                .setDomain(HOST)
                .addPathHandler("/", new AppAssets(new WebViewAssetLoader.AssetsPathHandler(this)))
                .build();

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                Uri url = request.getUrl();
                if (isAppUrl(url)) {
                    WebResourceResponse response = assetLoader.shouldInterceptRequest(url);
                    if (response != null) {
                        return response;
                    }
                }
                // Nothing outside the bundled assets is ever loaded inside the app.
                return blocked();
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri url = request.getUrl();
                if (isAppUrl(url)) {
                    return false;
                }
                // Only explicit https links (the "Actualizar ALLEN" download) leave the app, and
                // always to the browser; other schemes (intent:, file:, content:…) are ignored.
                if ("https".equals(url.getScheme())) {
                    Intent intent = new Intent(Intent.ACTION_VIEW, url);
                    intent.addCategory(Intent.CATEGORY_BROWSABLE);
                    try {
                        startActivity(intent);
                    } catch (ActivityNotFoundException ignored) {
                        // No app can open this link; stay in ALLEN.
                    }
                }
                return true;
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onPermissionRequest(PermissionRequest request) {
                request.deny();
            }

            @Override
            public void onGeolocationPermissionsShowPrompt(String origin, GeolocationPermissions.Callback callback) {
                callback.invoke(origin, false, false);
            }

            @Override
            public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
                if (fileCallback != null) {
                    fileCallback.onReceiveValue(null);
                }
                fileCallback = callback;
                // Only progress copies (.json) are imported. File managers label JSON inconsistently,
                // so let the user pick any document; the page validates size and content.
                Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.setType("*/*");
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

    private static boolean isAppUrl(Uri url) {
        return "https".equals(url.getScheme()) && HOST.equals(url.getHost());
    }

    private static WebResourceResponse blocked() {
        return new WebResourceResponse("text/plain", "utf-8", 403, "Forbidden", null,
                new ByteArrayInputStream(new byte[0]));
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
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        webView.destroy();
        super.onDestroy();
    }

    /** Serves the mobile experience; "/" and "/index.html" open it, nothing else is remapped. */
    private static final class AppAssets implements WebViewAssetLoader.PathHandler {
        private final WebViewAssetLoader.AssetsPathHandler assets;

        AppAssets(WebViewAssetLoader.AssetsPathHandler assets) {
            this.assets = assets;
        }

        @Override
        public WebResourceResponse handle(String path) {
            String file = path.isEmpty() || path.equals("index.html") ? "mobile/index.html" : path;
            return assets.handle("www/" + file);
        }
    }
}
