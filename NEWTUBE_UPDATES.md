# NewTube updates

NewTube is installed separately from SmartTube. Keep the original NewTube signing key: an
APK signed with a different key cannot update the installed app or retain its private data.
The signing key lives outside Git in `~/.config/newtube/signing`. Back up that directory securely.

Stable and beta look for `newtube_stable.json` and `newtube_beta.json` respectively in the
latest release of `arinaggarwal1/SmartTube`. Publish the matching signed APK and generated JSON
as assets of that release. The metadata generator verifies the APK is signed and has the right
application ID and pinned certificate:

```sh
python3 tools/make_update_manifest.py --apk path/to/NewTube_stable_version_armeabi-v7a.apk \
  --channel stable --tag YOUR_RELEASE_TAG --aapt /path/to/aapt --apksigner /path/to/apksigner
```

Upload both files to the release. Increment `versionCode` for every published update; changing
only the version name does not trigger an update. The latest release must contain metadata for
every channel you want to update. Until the first release exists, checks cannot find an update.
Android verifies the APK signing identity when it installs an update.
