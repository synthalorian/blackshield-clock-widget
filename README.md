# Blackshield Clock

A gothic medieval clock widget for Android. Blackletter time, a blood-red divide, cold steel date — mercenary livery for your home screen.

![Blackshield Clock over the Blackshield knight wallpaper](docs/preview.png)

## Features

- **Pirata One** blackletter typeface, bundled — no engine, no theming app required
- Bone-white time `#E8E6E3`, blood-red divider `#C1121F`, steel-gray date `#9BA0A6`
- Transparent background — your wallpaper shows through
- **Bulletproof rendering:** the clock face is drawn to a bitmap inside the app and handed to the launcher as a plain `ImageView` — no custom-font RemoteViews, no "Problem loading widget"
- Minute-accurate self-rescheduling tick; recovers on time/timezone/date changes
- Zero permissions, zero services, ~34 KB

## Install

1. Grab the APK from [Releases](../../releases)
2. Sideload it (allow "install unknown apps" when prompted)
3. Long-press home screen → **Widgets** → **Blackshield Clock** → drag to the field

**Recommended:** Settings → Apps → Blackshield Clock → **Alarms & reminders** → Allow. Android 14+ denies exact alarms by default; without it the widget falls back to inexact ticks and may lag a minute after deep doze.

## Build

```bash
gradle assembleDebug
```

Requires Android SDK (compileSdk 36), JDK 17+, Gradle 8.10+. Output: `app/build/outputs/apk/debug/app-debug.apk`.

## Design canon

Part of the **Blackshield** theme family (see [cachyos-blackshield](https://github.com/synthalorian/cachyos-blackshield) for the full Linux desktop livery):

| Token | Value |
|---|---|
| Blood accent | `#C1121F` |
| Bone text | `#E8E6E3` |
| Steel gray | `#9BA0A6` |
| Typeface | Pirata One (OFL) |

## License

Apache-2.0. Pirata One © The Pirata Project Authors, SIL Open Font License 1.1.

---

Made by synth with blackclaw ⚫🦞
