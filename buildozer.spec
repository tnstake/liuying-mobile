[app]
title = 流萤
package.name = liuying
package.domain = org.liuying.ai
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,db
version = 1.0.0
requirements = python3,kivy,requests,sqlite3
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,RECORD_AUDIO
android.api = 33
android.minapi = 24
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True
android.apptheme = @android:style/Theme.Material.Light.NoActionBar

[buildozer]
log_level = 2
warn_on_root = 1
