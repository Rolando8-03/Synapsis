#!/usr/bin/env bash
set -euo pipefail

package=io.github.rolando803.synapsis
adb shell svc wifi disable
adb shell svc data disable
adb install build/android/Synapsis-Android.apk
adb shell am start -W -n "$package/.MainActivity" | tee "$RUNNER_TEMP/synapsis-android-arranque.txt"
grep -Eq '^Status: ok' "$RUNNER_TEMP/synapsis-android-arranque.txt"
adb shell pm path "$package"
for attempt in {1..12}; do
  adb shell uiautomator dump /sdcard/synapsis-android.xml >/dev/null || true
  if adb shell cat /sdcard/synapsis-android.xml > "$RUNNER_TEMP/synapsis-android.xml" &&
    grep -q 'class="android.webkit.WebView"' "$RUNNER_TEMP/synapsis-android.xml" &&
    grep -q 'Synapsis' "$RUNNER_TEMP/synapsis-android.xml"; then
    adb shell getprop ro.build.version.sdk
    adb shell dumpsys webviewupdate | sed -n '/Current WebView package/p'
    exit 0
  fi
  sleep 2
done
echo 'El APK se instaló, pero no se observó la portada en WebView.' >&2
exit 1
