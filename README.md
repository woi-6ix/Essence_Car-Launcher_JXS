# JXS Essence Car Launcher

![Android](https://img.shields.io/badge/Platform-Android-green)
![Kotlin](https://img.shields.io/badge/Language-Kotlin-purple)
![Jetpack Compose](https://img.shields.io/badge/UI-Jetpack%20Compose-blue)
![Build](https://img.shields.io/badge/Build-GitHub%20Actions-black)
![Pages](https://img.shields.io/badge/Home%20Pages-3-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active%20Development-red)

**JXS Essence Car Launcher** is a customized Android automotive launcher based on **Essence / OpenLauncher**, designed for aftermarket Android head units and tablet-style in-car displays.

This JXS build extends the original launcher with a three-page swipeable home screen, independent widget layouts, improved map connectivity over cellular data, cleaner app-library behavior, and a reproducible automated APK build workflow.

Repository: [https://github.com/woi-6ix/Essence_Car-Launcher_JXS](https://github.com/woi-6ix/Essence_Car-Launcher_JXS)

---

## Project Overview

JXS Essence is maintained as a customization layer on top of the upstream OpenLauncher project.

Instead of duplicating the full Android source tree, this repository pins a known upstream revision and applies the JXS modifications automatically during the build process.

Current upstream revision:

```text
f2ef3903207ef712de1cd850d8ad3b14cfadd5fc
```

The GitHub Actions workflow:

1. Checks out this JXS repository.
2. Checks out the pinned upstream OpenLauncher source.
3. Applies the JXS patch.
4. Builds the Android application with Gradle.
5. Renames the generated APK.
6. Uploads the installable APK as a GitHub Actions artifact.

This keeps the JXS changes isolated, reviewable, and reproducible.

---

## What the Launcher Does

The launcher is intended to act as the primary dashboard interface for an Android-based vehicle display.

### Three Independent Home Pages

- Page 1 preserves the original Essence widget layout.
- Pages 2 and 3 begin empty.
- Swipe horizontally between all three pages.
- Each page stores its own widget configuration.
- The same widget type can appear on multiple pages.

### Page-Aware Widget Editing

Widget operations affect only the currently active page:

- Add widget
- Remove widget
- Drag widget
- Resize widget
- Open the Widget Library

Horizontal page swiping is disabled while widget editing is active so drag gestures do not accidentally change pages.

### Improved Map Connectivity

The original map widget specifically checked for Wi-Fi.

The JXS build instead accepts any validated Android Internet connection, including:

- Wi-Fi
- Cellular / LTE / 5G
- Ethernet
- Other validated network transports

### Cleaner All Apps View

The JXS App Library behaves more like a conventional Android launcher.

It queries apps that expose:

```text
Intent.ACTION_MAIN
Intent.CATEGORY_LAUNCHER
```

This removes hidden services, providers, and non-launchable internal Android packages from the normal All Apps screen.

---

## Key Features

- **Three swipeable dashboard pages**  
  Expands the original home screen into three independently managed layouts.

- **Independent widget layouts**  
  Moving, adding, removing, or resizing a widget only affects the active page.

- **Repeat widgets across pages**  
  Supported widgets can remain active on more than one home page.

- **Edit-safe page navigation**  
  Horizontal swiping is disabled while edit mode is active.

- **Cellular-compatible map widget**  
  Map connectivity is no longer limited to Wi-Fi-only checks.

- **Cleaner app drawer**  
  All Apps focuses on launchable apps rather than every installed package.

- **Persistent page layouts**  
  Page 2 and Page 3 layouts are stored independently using the existing settings system.

- **Automated APK builds**  
  GitHub Actions applies the JXS changes and produces an installable debug APK.

- **Original Essence styling preserved**  
  The JXS build extends the existing automotive UI instead of replacing its visual identity.

---

## Home Page Architecture

JXS expands the original single-home-screen layout into three independently persisted pages.

| Page | Default State | Storage |
| --- | --- | --- |
| Page 1 | Original Essence layout | `widget_layout_json` |
| Page 2 | Empty | `widget_layout_page2_json` |
| Page 3 | Empty | `widget_layout_page3_json` |

The home screen uses Jetpack Compose horizontal paging:

```text
HomeScreen
│
└── HorizontalPager
    ├── Page 1
    │   └── Independent Widget Grid
    ├── Page 2
    │   └── Independent Widget Grid
    └── Page 3
        └── Independent Widget Grid
```

Each widget operation includes the current page index so updates remain isolated to the correct layout.

---

## Widget Management

| Action | JXS Behavior |
| --- | --- |
| Add Widget | Current page only |
| Remove Widget | Current page only |
| Drag Widget | Current page only |
| Resize Widget | Current page only |
| Widget Library State | Current page |
| Same Widget on Multiple Pages | Supported |
| Swipe During Normal Use | Enabled |
| Swipe During Edit Mode | Disabled |

When a widget is removed from one page, its global visibility flag is only disabled if that widget is no longer enabled on any of the three pages.

---

## Map and Connectivity Changes

The map widget now checks whether the active Android network has both:

```text
NET_CAPABILITY_INTERNET
NET_CAPABILITY_VALIDATED
```

This is more appropriate for dedicated automotive Android devices that may use their own cellular modem instead of Wi-Fi.

### GPS Requirement

Internet connectivity and GPS are separate.

The following features require Android to provide a valid location fix:

- Map positioning
- Weather location
- Speedometer
- Altimeter
- Trip tracking
- Compass / heading behavior

When testing on the Android Studio Emulator, simulated GPS may need to be injected manually because the emulator does not automatically inherit the computer's physical location.

A physical Android head unit with working GPS hardware does not require this emulator-specific setup.

---

## App Library Behavior

The upstream source intentionally queried all installed applications, including packages without launcher activities.

The JXS build changes the normal All Apps experience to focus on apps that can actually be launched from a standard Android launcher.

This generally excludes:

- Hidden system services
- Background-only packages
- Internal framework components
- Providers
- Packages without a launcher activity

Normal preinstalled applications with a standard launcher entry may still appear.

---

## Project Structure

```text
Essence_Car-Launcher_JXS/
│
├── .github/
│   └── workflows/
│       └── build-apk.yml
│
├── patches/
│   └── apply_patch.py
│
├── Essence-Launcher-1.0.0-essence.1.apk
├── LICENSE
└── README.md
```

| File | Purpose |
| --- | --- |
| `patches/apply_patch.py` | Applies all current JXS modifications to the pinned upstream source |
| `.github/workflows/build-apk.yml` | Automated Android build pipeline |
| `README.md` | Project documentation |
| `LICENSE` | MIT license |
| `Essence-Launcher-1.0.0-essence.1.apk` | Original/reference APK stored in the repository |

---

## Tech Stack

| Category | Technology |
| --- | --- |
| Platform | Android |
| Language | Kotlin |
| UI | Jetpack Compose |
| Persistence | Android DataStore |
| Build System | Gradle |
| Java Runtime | Temurin Java 17 |
| CI/CD | GitHub Actions |
| Patch Layer | Python 3 |
| Upstream | Essence / OpenLauncher |
| Target | Automotive head units and landscape Android displays |

---

## APK Build Workflow

The repository includes a GitHub Actions workflow named:

```text
Build Essence JXS APK
```

It runs automatically when changes are pushed to `main` and can also be started manually from the **Actions** tab.

### Build Flow

```text
JXS Repository
      │
      ▼
Checkout pinned OpenLauncher revision
      │
      ▼
Apply patches/apply_patch.py
      │
      ▼
Gradle assembleDebug
      │
      ▼
Rename APK
      │
      ▼
Upload GitHub Actions artifact
```

The generated APK is renamed to:

```text
Essence-Launcher-1.0.0-essence-jxs.apk
```

The GitHub Actions artifact is named:

```text
Essence-Launcher-JXS-APK
```

---

## Building Locally

### 1. Clone the JXS Repository

```bash
git clone https://github.com/woi-6ix/Essence_Car-Launcher_JXS.git
cd Essence_Car-Launcher_JXS
```

### 2. Clone the Pinned Upstream Source

```bash
git clone https://github.com/vickoc911/openlauncher.git upstream
cd upstream
git checkout f2ef3903207ef712de1cd850d8ad3b14cfadd5fc
cd ..
```

### 3. Apply the JXS Patch

```bash
python patches/apply_patch.py upstream
```

### 4. Build the APK

**Windows**

```powershell
cd upstream
.\gradlew.bat assembleDebug
```

**macOS / Linux**

```bash
cd upstream
chmod +x gradlew
./gradlew assembleDebug
```

The debug APK is normally generated at:

```text
upstream/app/build/outputs/apk/debug/app-debug.apk
```

---

## Installing the APK

For a first install with ADB:

```bash
adb install app-debug.apk
```

To replace an existing compatible build:

```bash
adb install -r app-debug.apk
```

### Signing Note

The automated GitHub Actions workflow currently produces a **debug APK**.

Android only allows an installed package to be upgraded when the new APK is signed with a compatible signing key.

If Android reports a signature mismatch, the previous build may need to be uninstalled before installing the new debug APK.

Uninstalling the app also removes its locally stored launcher settings.

---

## Using the Three-Page Launcher

1. Launch JXS Essence.
2. Page 1 opens with the original Essence widget layout.
3. Swipe horizontally to Page 2 or Page 3.
4. Enter widget edit mode.
5. Open the Widget Library.
6. Add widgets to the current page.
7. Drag and resize widgets as needed.
8. Exit edit mode.
9. Swipe between pages normally.

Changes made on one page do not rearrange the other two pages.

---

## Internet and Location Requirements

| Feature | Main Requirement |
| --- | --- |
| Map Tiles | Valid Internet connection |
| Weather | Internet + location |
| GPS Map Position | Android location fix |
| Speedometer | GPS |
| Altimeter | GPS |
| Trip Tracker | GPS |
| Online Map Provider | Internet + location for positioning |

A working Internet connection does not automatically mean that GPS is working, and a valid GPS fix does not automatically mean that map tiles have Internet access.

---

## Known Limitations

### Debug Signing

The current automated workflow produces debug builds rather than production-signed release APKs.

### Emulator GPS

Android Studio virtual devices may fail to continuously emit simulated GPS fixes even when a route has been imported into Extended Controls.

This is an emulator/testing issue and is not representative of a physical head unit with functional GPS hardware.

### Google Maps Navigation Embedding

The current map widget is not the full consumer Google Maps application embedded inside the launcher.

Launching Google Maps navigation, displaying a native map, and embedding full turn-by-turn navigation are separate Android integration approaches.

### Pinned Upstream Revision

The JXS patch is intentionally written against:

```text
f2ef3903207ef712de1cd850d8ad3b14cfadd5fc
```

Moving to a newer upstream revision may require updating patch anchors if source files have changed.

---

## Troubleshooting

### Maps or Weather Do Not Detect Location

Check that:

- Android Location is enabled.
- Essence has location permission.
- Precise location is enabled when supported by the device.
- The device or emulator is producing an actual location fix.
- Internet access is available for online map tiles and weather data.

### Emulator Shows No GPS Updates

Use Android Studio Extended Controls to inject a location or route.

If the emulator still reports no location fixes, ADB test providers can be used during development to inject mock GPS coordinates.

### All Apps Shows Unexpected Packages

The JXS build only queries apps with a standard launcher activity. A legitimate preinstalled system app may still appear if it exposes a normal launcher entry.

### APK Will Not Install Over an Existing Build

A signing mismatch between debug APKs can prevent Android from performing an in-place upgrade.

Uninstall the previous incompatible build and install the new APK, or use a stable signing configuration for repeat upgrades.

---

## Current JXS Changes

The current patch modifies the upstream project in the following areas:

| Area | Change |
| --- | --- |
| Map Widget | Accept validated Wi-Fi, cellular, Ethernet, or other Internet transports |
| Home Screen | Three horizontally swipeable pages |
| Widget Layout | Separate Page 1, Page 2, and Page 3 configuration |
| Widget Editing | Page-aware add, remove, move, and resize |
| Widget Library | Reflects current-page state |
| Pager Gestures | Disabled during edit mode |
| App Library | Standard launchable applications only |
| Settings | Additional persisted page-layout keys |
| Build Version | JXS version metadata |
| CI | Automated GitHub Actions APK build |

---

## Future Improvements

Potential JXS upgrades include:

- Native navigation-focused map experience
- Google Maps navigation handoff improvements
- More automotive-focused widgets
- Stable release signing
- Improved large-screen responsiveness
- Additional head-unit-specific integrations
- Better app categorization
- Page indicators and page customization
- Saved launcher layout profiles
- Improved GPS and emulator testing tools

---

## Upstream Project

JXS Essence is based on the open-source **OpenLauncher / Essence** project by its upstream contributors.

Upstream repository:

[https://github.com/vickoc911/openlauncher](https://github.com/vickoc911/openlauncher)

The JXS project focuses on customized automotive behavior and workflow changes while preserving the upstream launcher's core design and functionality.

---

## Author

**Woi-6ix**

Built as a customized Android automotive launcher project focused on multi-page widget layouts, head-unit usability, connectivity, GPS-based widgets, and automated Android build workflows.

---

## License

This repository is licensed under the **MIT License**.

See the included `LICENSE` file for details.
