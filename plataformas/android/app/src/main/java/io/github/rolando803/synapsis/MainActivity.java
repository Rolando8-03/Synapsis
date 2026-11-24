package io.github.rolando803.synapsis;

import android.app.Activity;
import android.content.pm.ApplicationInfo;
import android.graphics.Color;
import android.os.Bundle;
import android.net.Uri;
import android.view.WindowInsets;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.webkit.WebViewAssetLoader;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.URLConnection;
import java.util.Collections;

public final class MainActivity extends Activity {
    private static final String HOST = WebViewAssetLoader.DEFAULT_DOMAIN;
    private static final String PREFIX = "/synapsis/";
    private WebView web;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        web = new WebView(this);
        web.setBackgroundColor(Color.rgb(13,25,41));
        web.setOnApplyWindowInsetsListener((view,insets) -> {
            if (android.os.Build.VERSION.SDK_INT >= 35) {
                android.graphics.Insets system = insets.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout());
                view.setPadding(system.left,system.top,system.right,system.bottom);
            }
            return insets;
        });
        setContentView(web);
        WebView.setWebContentsDebuggingEnabled((getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE) != 0);
        WebSettings settings = web.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setSupportZoom(true);
        settings.setBuiltInZoomControls(true);
        settings.setDisplayZoomControls(false);
        final WebViewAssetLoader assets = new WebViewAssetLoader.Builder()
            .addPathHandler(PREFIX, this::asset)
            .build();
        web.setWebViewClient(new WebViewClient() {
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                Uri url = request.getUrl();
                if (local(url) && request.getMethod().equals("GET")) {
                    WebResourceResponse localFile = assets.shouldInterceptRequest(url);
                    if (localFile != null) return localFile;
                }
                return missing();
            }

            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri url = request.getUrl();
                if (local(url)) return false;
                if (request.isForMainFrame() && "https".equals(url.getScheme())) {
                    try { startActivity(new android.content.Intent(android.content.Intent.ACTION_VIEW,url)); }
                    catch (android.content.ActivityNotFoundException ignored) { }
                }
                return true;
            }
        });
        if (state == null || web.restoreState(state) == null) web.loadUrl("https://" + HOST + PREFIX + "index.html");
    }

    private static boolean local(Uri url) {
        String path = url.getPath();
        return "https".equals(url.getScheme()) && HOST.equals(url.getHost())
            && (url.getPort() == -1 || url.getPort() == 443) && path != null && path.startsWith(PREFIX);
    }

    private WebResourceResponse asset(String path) {
        if (path.isEmpty()) path = "index.html";
        for (String part : path.split("/")) {
            if (part.equals("..") || part.equals(".") || part.indexOf(92) >= 0) return missing();
        }
        String mime;
        if (path.endsWith(".wasm")) mime = "application/wasm";
        else if (path.endsWith(".js") || path.endsWith(".mjs")) mime = "text/javascript";
        else if (path.endsWith(".json")) mime = "application/json";
        else if (path.endsWith(".svg")) mime = "image/svg+xml";
        else if (path.endsWith(".webp")) mime = "image/webp";
        else if (path.endsWith(".woff2")) mime = "font/woff2";
        else {
            mime = URLConnection.guessContentTypeFromName(path);
            if (mime == null) mime = "application/octet-stream";
        }
        try {
            InputStream data = getAssets().open(path);
            boolean text = mime.startsWith("text/") || mime.equals("application/json") || mime.equals("image/svg+xml");
            return new WebResourceResponse(mime,text ? "UTF-8" : null,200,"OK",
                    Collections.singletonMap("X-Content-Type-Options","nosniff"),data);
        } catch (IOException error) {
            return missing();
        }
    }

    private static WebResourceResponse missing() {
        return new WebResourceResponse("text/plain","UTF-8",404,"Not Found",Collections.emptyMap(),
                new ByteArrayInputStream(new byte[0]));
    }

    @Override protected void onSaveInstanceState(Bundle state) {
        web.saveState(state);
        super.onSaveInstanceState(state);
    }

    @Override public void onBackPressed() {
        if (web.canGoBack()) web.goBack(); else super.onBackPressed();
    }

    @Override protected void onPause() {
        web.evaluateJavascript("dispatchEvent(new Event('synapsis:pause'))",null);
        web.onPause();
        super.onPause();
    }

    @Override protected void onResume() {
        super.onResume();
        web.onResume();
    }

    @Override protected void onDestroy() {
        web.destroy();
        super.onDestroy();
    }
}
