#!/usr/bin/env python3
from pathlib import Path
import re
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_patch.py <openlauncher-source-root>")

ROOT = Path(sys.argv[1]).resolve()

def load(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        raise SystemExit(f"Missing expected source file: {rel}")
    return p.read_text(encoding="utf-8")

def save(rel: str, text: str) -> None:
    (ROOT / rel).write_text(text, encoding="utf-8")

def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"Patch anchor {label!r}: expected exactly 1 match, found {n}")
    return text.replace(old, new, 1)

rel = "app/src/main/java/com/openlauncher/app/ui/widget/MapWidget.kt"
s = load(rel)
s = replace_once(
    s,
    '''    // --- Auxiliar para verificar estado del Wi-Fi ---
    fun isWifiConnected(ctx: Context): Boolean {
        val cm = ctx.getSystemService(Context.CONNECTIVITY_SERVICE) as? ConnectivityManager
        val network = cm?.activeNetwork ?: return false
        val capabilities = cm.getNetworkCapabilities(network) ?: return false
        return capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)
    }

    // Monitoreamos reactivamente si hay Wi-Fi disponible
    var hasWifi by remember { mutableStateOf(isWifiConnected(context)) }
''',
    '''    // Any validated Internet connection is usable: Wi-Fi, cellular, Ethernet, etc.
    fun isOnline(ctx: Context): Boolean {
        val cm = ctx.getSystemService(Context.CONNECTIVITY_SERVICE) as? ConnectivityManager
        val caps = cm?.getNetworkCapabilities(cm.activeNetwork) ?: return false
        return caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) &&
            caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
    }

    // Monitor whether the active network can actually reach the Internet.
    var hasConnection by remember { mutableStateOf(isOnline(context)) }
''',
    "MapWidget connectivity helper",
)
s = s.replace("isWifiConnected(context)", "isOnline(context)")
s = s.replace("hasWifi", "hasConnection")
save(rel, s)

rel = "app/src/main/java/com/openlauncher/app/data/AppSettings.kt"
s = load(rel)
s = replace_once(
    s,
    "const val GRID_ROWS = 2\n",
    "const val GRID_ROWS = 2\nconst val HOME_PAGE_COUNT = 3\n",
    "HOME_PAGE_COUNT",
)
s = replace_once(
    s,
    "    val widgetLayout: List<WidgetConfig> = defaultWidgetLayout(),\n",
    "    val widgetLayout: List<WidgetConfig> = defaultWidgetLayout(),\n"
    "    val widgetLayoutPage2: List<WidgetConfig> = emptyList(),\n"
    "    val widgetLayoutPage3: List<WidgetConfig> = emptyList(),\n",
    "page layout fields",
)
page_helpers = '''fun AppSettings.widgetLayoutForPage(pageIndex: Int): List<WidgetConfig> = when (pageIndex) {
    0 -> widgetLayout
    1 -> widgetLayoutPage2
    2 -> widgetLayoutPage3
    else -> emptyList()
}

fun AppSettings.withWidgetLayoutForPage(
    pageIndex: Int,
    layout: List<WidgetConfig>
): AppSettings = when (pageIndex) {
    0 -> copy(widgetLayout = layout)
    1 -> copy(widgetLayoutPage2 = layout)
    2 -> copy(widgetLayoutPage3 = layout)
    else -> this
}

fun AppSettings.allWidgetLayouts(): List<List<WidgetConfig>> =
    listOf(widgetLayout, widgetLayoutPage2, widgetLayoutPage3)

'''
s = replace_once(
    s,
    "fun AppSettings.activeWidgetIds(): Set<String> = buildSet {\n",
    page_helpers + "fun AppSettings.activeWidgetIds(): Set<String> = buildSet {\n",
    "page layout helpers",
)
save(rel, s)

rel = "app/src/main/java/com/openlauncher/app/data/SettingsRepository.kt"
s = load(rel)
s = replace_once(
    s,
    '        val WIDGET_LAYOUT_JSON = stringPreferencesKey("widget_layout_json")\n',
    '        val WIDGET_LAYOUT_JSON       = stringPreferencesKey("widget_layout_json")\n'
    '        val WIDGET_LAYOUT_PAGE2_JSON = stringPreferencesKey("widget_layout_page2_json")\n'
    '        val WIDGET_LAYOUT_PAGE3_JSON = stringPreferencesKey("widget_layout_page3_json")\n',
    "page DataStore keys",
)
read_pages = '''
            val widgetsPage2 = prefs[Keys.WIDGET_LAYOUT_PAGE2_JSON]?.let { json ->
                runCatching {
                    gson.fromJson<List<WidgetConfig>>(
                        json,
                        object : TypeToken<List<WidgetConfig>>() {}.type
                    )
                }.getOrNull()
            } ?: emptyList()

            val widgetsPage3 = prefs[Keys.WIDGET_LAYOUT_PAGE3_JSON]?.let { json ->
                runCatching {
                    gson.fromJson<List<WidgetConfig>>(
                        json,
                        object : TypeToken<List<WidgetConfig>>() {}.type
                    )
                }.getOrNull()
            } ?: emptyList()
'''
s = replace_once(
    s,
    "            } else defaults.widgetLayout\n\n            return AppSettings(\n",
    "            } else defaults.widgetLayout\n" + read_pages + "\n            return AppSettings(\n",
    "read page layouts",
)
s = replace_once(
    s,
    "                widgetLayout   = widgets,\n",
    "                widgetLayout      = widgets,\n"
    "                widgetLayoutPage2 = widgetsPage2,\n"
    "                widgetLayoutPage3 = widgetsPage3,\n",
    "AppSettings page assignments",
)
s = replace_once(
    s,
    "            prefs[Keys.WIDGET_LAYOUT_JSON] = gson.toJson(s.widgetLayout)\n",
    "            prefs[Keys.WIDGET_LAYOUT_JSON]       = gson.toJson(s.widgetLayout)\n"
    "            prefs[Keys.WIDGET_LAYOUT_PAGE2_JSON] = gson.toJson(s.widgetLayoutPage2)\n"
    "            prefs[Keys.WIDGET_LAYOUT_PAGE3_JSON] = gson.toJson(s.widgetLayoutPage3)\n",
    "write page layouts",
)
save(rel, s)

rel = "app/src/main/java/com/openlauncher/app/viewmodel/LauncherViewModel.kt"
s = load(rel)
s = replace_once(
    s,
    "import com.openlauncher.app.data.defaultShortcuts\n",
    "import com.openlauncher.app.data.defaultShortcuts\n"
    "import com.openlauncher.app.data.widgetLayoutForPage\n"
    "import com.openlauncher.app.data.withWidgetLayoutForPage\n"
    "import com.openlauncher.app.data.allWidgetLayouts\n",
    "ViewModel page helper imports",
)
replacement = r'''    fun updateWidgetConfig(pageIndex: Int, id: String, spanX: Int, spanY: Int) {
        updateSettings {
            val pageLayout = widgetLayoutForPage(pageIndex)
            val resized = pageLayout.map { w ->
                if (w.id == id) w.copy(
                    spanX = spanX.coerceIn(1, GRID_COLS - w.gridX),
                    spanY = spanY.coerceIn(1, GRID_ROWS - w.gridY)
                ) else w
            }
            val activeIds = activeWidgetIds()
            val active    = resized.filter { it.enabled && it.id in activeIds }
            val inactive  = resized.filter { !it.enabled || it.id !in activeIds }
            val target    = active.find { it.id == id }
            val newLayout = if (target != null) {
                computeWidgetMove(active, id, target.gridX, target.gridY) + inactive
            } else {
                resized
            }
            withWidgetLayoutForPage(pageIndex, newLayout)
        }
    }

    fun moveWidgetConfig(pageIndex: Int, id: String, gridX: Int, gridY: Int) {
        updateSettings {
            val pageLayout = widgetLayoutForPage(pageIndex)
            val activeIds  = activeWidgetIds()
            val active     = pageLayout.filter { it.enabled && it.id in activeIds }
            val inactive   = pageLayout.filter { !it.enabled || it.id !in activeIds }
            withWidgetLayoutForPage(
                pageIndex,
                computeWidgetMove(active, id, gridX, gridY) + inactive
            )
        }
    }

    fun addWidget(pageIndex: Int, id: String) {
        updateSettings {
            val activeIds = activeWidgetIds()
            var layout    = widgetLayoutForPage(pageIndex)
            var cell      = freeCellIn(layout, activeIds)

            if (cell == null) {
                val candidate = layout
                    .filter { it.enabled && it.id in activeIds && it.spanX * it.spanY > 1 }
                    .maxByOrNull { it.spanX * it.spanY }
                if (candidate != null) {
                    layout = layout.map { w ->
                        if (w.id == candidate.id) {
                            if (w.spanY > 1) w.copy(spanY = w.spanY - 1)
                            else w.copy(spanX = w.spanX - 1)
                        } else w
                    }
                    cell = freeCellIn(layout, activeIds)
                }
            }

            val freeCell = cell ?: return@updateSettings this

            val withShow = when (id) {
                "CLOCK"        -> copy(showClock = true)
                "WEATHER"      -> copy(showWeather = true)
                "NOW_PLAYING"  -> copy(showNowPlaying = true)
                "TELEMETRY"    -> copy(showTelemetry = true)
                "ALTIMETER"    -> copy(showAltimeter = true)
                "SPEEDOMETER"  -> copy(showSpeedometer = true)
                "VITALS"       -> copy(showVitals = true)
                "TRIP_TRACKER" -> copy(showTripTracker = true)
                "SOUNDBOARD"   -> copy(showSoundboard = true)
                "MAP"          -> copy(showMap = true)
                else           -> this
            }

            val idx = layout.indexOfFirst { it.id == id }
            val newLayout = if (idx >= 0) {
                layout.toMutableList().also { list ->
                    val w = list[idx]
                    val area = if (w.spanX > 1 || w.spanY > 1) {
                        freeAreaIn(layout, activeIds, w.spanX, w.spanY)
                    } else null
                    list[idx] = if (area != null) {
                        w.copy(enabled = true, gridX = area.first, gridY = area.second)
                    } else {
                        w.copy(
                            enabled = true,
                            gridX = freeCell.first,
                            gridY = freeCell.second,
                            spanX = 1,
                            spanY = 1
                        )
                    }
                }
            } else {
                layout + com.openlauncher.app.data.WidgetConfig(
                    id,
                    freeCell.first,
                    freeCell.second
                )
            }

            withShow.withWidgetLayoutForPage(pageIndex, newLayout)
        }
    }

    fun toggleMapProvider() {
        updateSettings {
            copy(mapProvider = if (mapProvider == MapProvider.OSM) MapProvider.GOOGLE else MapProvider.OSM)
        }
    }

    fun removeWidget(pageIndex: Int, id: String) {
        updateSettings {
            val updatedPage = widgetLayoutForPage(pageIndex).map { w ->
                if (w.id == id) w.copy(enabled = false) else w
            }
            val updatedSettings = withWidgetLayoutForPage(pageIndex, updatedPage)
            val stillUsed = updatedSettings.allWidgetLayouts().any { page ->
                page.any { it.enabled && it.id == id }
            }

            if (stillUsed) {
                updatedSettings
            } else {
                when (id) {
                    "CLOCK"        -> updatedSettings.copy(showClock = false)
                    "WEATHER"      -> updatedSettings.copy(showWeather = false)
                    "NOW_PLAYING"  -> updatedSettings.copy(showNowPlaying = false)
                    "TELEMETRY"    -> updatedSettings.copy(showTelemetry = false)
                    "ALTIMETER"    -> updatedSettings.copy(showAltimeter = false)
                    "SPEEDOMETER"  -> updatedSettings.copy(showSpeedometer = false)
                    "VITALS"       -> updatedSettings.copy(showVitals = false)
                    "TRIP_TRACKER" -> updatedSettings.copy(showTripTracker = false)
                    "SOUNDBOARD"   -> updatedSettings.copy(showSoundboard = false)
                    "MAP"          -> updatedSettings.copy(showMap = false)
                    else           -> updatedSettings
                }
            }
        }
    }

'''
s, n = re.subn(
    r"    fun updateWidgetConfig\(.*?(?=    fun updateSoundboardPad\()",
    replacement,
    s,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit(f"ViewModel widget operation block: expected 1 replacement, found {n}")
save(rel, s)

rel = "app/src/main/java/com/openlauncher/app/ui/screen/HomeScreen.kt"
s = load(rel)
s = replace_once(
    s,
    "import androidx.compose.foundation.lazy.grid.items\n",
    "import androidx.compose.foundation.lazy.grid.items\n"
    "import androidx.compose.foundation.pager.HorizontalPager\n"
    "import androidx.compose.foundation.pager.rememberPagerState\n",
    "pager imports",
)
s = replace_once(
    s,
    "import com.openlauncher.app.data.WidgetConfig\n",
    "import com.openlauncher.app.data.WidgetConfig\n"
    "import com.openlauncher.app.data.HOME_PAGE_COUNT\n"
    "import com.openlauncher.app.data.widgetLayoutForPage\n",
    "HomeScreen page imports",
)
s = replace_once(
    s,
    "private fun canAddWidget(settings: com.openlauncher.app.data.AppSettings): Boolean {\n",
    "private fun canAddWidget(\n"
    "    settings: com.openlauncher.app.data.AppSettings,\n"
    "    layout: List<WidgetConfig>\n"
    "): Boolean {\n",
    "canAddWidget signature",
)
s = replace_once(
    s,
    "    val activeWidgets = settings.widgetLayout.filter { it.enabled && it.id in visibleIds }\n",
    "    val activeWidgets = layout.filter { it.enabled && it.id in visibleIds }\n",
    "canAddWidget page layout",
)
s = replace_once(
    s,
    "    onUpdateWidget: (id: String, spanX: Int, spanY: Int) -> Unit,\n"
    "    onMoveWidget: (id: String, gridX: Int, gridY: Int) -> Unit,\n"
    "    onAddWidget: (id: String) -> Unit,\n"
    "    onRemoveWidget: (id: String) -> Unit,\n",
    "    onUpdateWidget: (pageIndex: Int, id: String, spanX: Int, spanY: Int) -> Unit,\n"
    "    onMoveWidget: (pageIndex: Int, id: String, gridX: Int, gridY: Int) -> Unit,\n"
    "    onAddWidget: (pageIndex: Int, id: String) -> Unit,\n"
    "    onRemoveWidget: (pageIndex: Int, id: String) -> Unit,\n",
    "page-aware HomeScreen callbacks",
)
s = replace_once(
    s,
    "    var widgetLibraryOpen by remember { mutableStateOf(false) }\n\n    Column(modifier = modifier.fillMaxSize()) {\n",
    "    var widgetLibraryOpen by remember { mutableStateOf(false) }\n"
    "    val pagerState = rememberPagerState(initialPage = 0) { HOME_PAGE_COUNT }\n\n"
    "    Column(modifier = modifier.fillMaxSize()) {\n",
    "pager state",
)
old_grid_start = '''        // ── Widget Grid ─────────────────────────────────────────────────────
        BoxWithConstraints(
            modifier = Modifier
                .fillMaxSize()
                .padding(gap)
        ) {
'''
new_grid_start = '''        // ── Widget Pages ────────────────────────────────────────────────────
        HorizontalPager(
            state = pagerState,
            userScrollEnabled = !editMode,
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
        ) { pageIndex ->
            val pageLayout = settings.widgetLayoutForPage(pageIndex)

            BoxWithConstraints(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(gap)
            ) {
'''
s = replace_once(s, old_grid_start, new_grid_start, "three-page pager grid")
s = replace_once(
    s,
    "            val visible = settings.widgetLayout.filter { it.enabled && it.id in visibleIds }\n",
    "            val visible = pageLayout.filter { it.enabled && it.id in visibleIds }\n",
    "page-specific visible widgets",
)
s = replace_once(
    s,
    "                                            onMoveWidget(w.id, newX, newY)\n",
    "                                            onMoveWidget(pageIndex, w.id, newX, newY)\n",
    "page-aware drag commit",
)
s = replace_once(
    s,
    "            }\n        }\n    }\n\n    // ── Widget context menu (long-press any cell) ────────────────────────────\n",
    "            }\n        }\n        }\n    }\n\n    // ── Widget context menu (long-press any cell) ────────────────────────────\n",
    "pager closing brace",
)
s = replace_once(
    s,
    "        val config = settings.widgetLayout.find { it.id == id }\n",
    "        val currentPageLayout = settings.widgetLayoutForPage(pagerState.currentPage)\n"
    "        val config = currentPageLayout.find { it.id == id }\n",
    "resize current-page layout",
)
s = replace_once(
    s,
    "                    onUpdateWidget(id, sx, sy)\n",
    "                    onUpdateWidget(pagerState.currentPage, id, sx, sy)\n",
    "page-aware resize commit",
)
s = replace_once(
    s,
    "        WidgetLibraryDialog(\n"
    "            settings  = settings,\n"
    "            accent    = accent,\n",
    "        WidgetLibraryDialog(\n"
    "            settings  = settings,\n"
    "            layout    = settings.widgetLayoutForPage(pagerState.currentPage),\n"
    "            accent    = accent,\n",
    "widget library current layout",
)
s = replace_once(
    s,
    "            onAdd     = { id -> onAddWidget(id) },\n"
    "            onRemove  = { id -> onRemoveWidget(id) },\n",
    "            onAdd     = { id -> onAddWidget(pagerState.currentPage, id) },\n"
    "            onRemove  = { id -> onRemoveWidget(pagerState.currentPage, id) },\n",
    "widget library page-aware callbacks",
)
s = replace_once(
    s,
    "private fun WidgetLibraryDialog(\n"
    "    settings: AppSettings,\n"
    "    accent: Color,\n",
    "private fun WidgetLibraryDialog(\n"
    "    settings: AppSettings,\n"
    "    layout: List<WidgetConfig>,\n"
    "    accent: Color,\n",
    "WidgetLibraryDialog layout parameter",
)
old_library_active = '''    val activeIds = buildSet {
        if (settings.showClock) add("CLOCK")
        if (settings.showWeather) add("WEATHER")
        if (settings.showNowPlaying) add("NOW_PLAYING")
        if (settings.showTelemetry) add("TELEMETRY")
        if (settings.showAltimeter) add("ALTIMETER")
        if (settings.showSpeedometer) add("SPEEDOMETER")
        if (settings.showVitals) add("VITALS")
        if (settings.showTripTracker) add("TRIP_TRACKER")
        if (settings.showSoundboard) add("SOUNDBOARD")
        if (settings.showMap) add("MAP")
    }
    val canAdd = canAddWidget(settings)
'''
new_library_active = '''    val activeIds = layout.filter { it.enabled }.mapTo(mutableSetOf()) { it.id }
    val canAdd = canAddWidget(settings, layout)
'''
s = replace_once(s, old_library_active, new_library_active, "page-specific widget library state")
save(rel, s)

rel = "app/src/main/java/com/openlauncher/app/MainActivity.kt"
s = load(rel)
s = replace_once(
    s,
    "                                        onUpdateWidget      = { id, sx, sy -> vm.updateWidgetConfig(id, sx, sy) },\n"
    "                                        onMoveWidget        = { id, gx, gy -> vm.moveWidgetConfig(id, gx, gy) },\n"
    "                                        onAddWidget         = { id -> vm.addWidget(id) },\n"
    "                                        onRemoveWidget      = { id -> vm.removeWidget(id) },\n",
    "                                        onUpdateWidget      = { page, id, sx, sy -> vm.updateWidgetConfig(page, id, sx, sy) },\n"
    "                                        onMoveWidget        = { page, id, gx, gy -> vm.moveWidgetConfig(page, id, gx, gy) },\n"
    "                                        onAddWidget         = { page, id -> vm.addWidget(page, id) },\n"
    "                                        onRemoveWidget      = { page, id -> vm.removeWidget(page, id) },\n",
    "MainActivity page-aware callbacks",
)
save(rel, s)

rel = "app/build.gradle.kts"
s = load(rel)
s = replace_once(s, '        versionCode    = 6\n', '        versionCode    = 7\n', "versionCode")
s = replace_once(s, '        versionName    = "0.0.5"\n', '        versionName    = "0.0.6-jxs"\n', "versionName")
save(rel, s)

print("Applied Essence JXS cellular-map + three-page widget patch successfully.")
