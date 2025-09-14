"""
human_browser.py
----------------
Wrapper autour de Playwright pour lancer un navigateur "humain".
- Lancement de Chrome avec un profil persistant Playwright (cookies, Google login après une fois)
- Patchs anti-détection (playwright-stealth ou JS custom)
- Fonctions utilitaires pour simuler des interactions humaines
"""

import random
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# Optionnel : stealth si installé
try:
    from playwright_stealth import stealth_sync
    HAS_STEALTH_SYNC = True
except ImportError:
    HAS_STEALTH_SYNC = False

# -----------------------------
# Config par défaut
# -----------------------------

USER_DATA_DIR = str(Path("userdata").absolute())  # Profil Playwright persistant
DEFAULT_LOCALE = "fr-FR"
DEFAULT_TIMEZONE = "Europe/Brussels"

# -----------------------------
# Stealth JS (mimique vrai Chrome)
# -----------------------------

STEALTH_JS = """
// --- Patch WebDriver ---
Object.defineProperty(navigator, 'webdriver', { get: () => false });

// --- Patch window.chrome ---
window.chrome = { runtime: {} };

// --- Patch languages ---
Object.defineProperty(navigator, "languages", {
    get: () => ["fr-FR", "fr", "en-US", "en"],
});

// --- Patch plugins ---
Object.defineProperty(navigator, 'plugins', {
    get: () => {
        return {
            length: 4,
            0: { name: "Chrome PDF Plugin", filename: "internal-pdf-viewer", description: "Portable Document Format" },
            1: { name: "Chrome PDF Viewer", filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai", description: "" },
            2: { name: "Native Client", filename: "internal-nacl-plugin", description: "" },
            3: { name: "Microsoft Edge PDF Viewer", filename: "internal-pdf-viewer", description: "Edge PDF Viewer" },
            item: function(i) { return this[i]; },
            namedItem: function(name) {
                for (let i = 0; i < this.length; i++) {
                    if (this[i].name === name) return this[i];
                }
                return null;
            }
        };
    },
});
"""

# -----------------------------
# Humanisation des timings
# -----------------------------

def human_delay(mu=0.3, sigma=0.15):
    """Pause gaussienne aléatoire"""
    delay = max(0.05, random.gauss(mu, sigma))
    time.sleep(delay)

# -----------------------------
# Humanisation des actions
# -----------------------------

def human_scroll(page, min_scroll=200, max_scroll=1000):
    """Scroll progressif avec pauses"""
    total_scroll = random.randint(min_scroll, max_scroll)
    step = random.randint(20, 80)
    for _ in range(0, total_scroll, step):
        page.mouse.wheel(0, step)
        human_delay(0.1, 0.05)

def human_click(page, selector):
    """Clic avec mouvement de souris réaliste"""
    box = page.locator(selector).bounding_box()
    if not box:
        return
    x = box["x"] + random.uniform(5, box["width"] - 5)
    y = box["y"] + random.uniform(5, box["height"] - 5)
    steps = random.randint(15, 30)
    page.mouse.move(x, y, steps=steps)
    human_delay(0.2, 0.1)
    page.mouse.click(x, y)

# -----------------------------
# Lancement du navigateur
# -----------------------------

def launch_browser():
    """
    Lance Chrome avec un profil persistant Playwright.
    La première fois → login Google à faire manuellement.
    Ensuite → session sauvegardée dans userdata/.
    """
    p = sync_playwright().start()

    context = p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        channel="chrome",          # utilise ton Chrome installé
        headless=False,
        args=[
            "--start-maximized",
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
        ],
        locale=DEFAULT_LOCALE,
        timezone_id=DEFAULT_TIMEZONE,
    )

    # Applique stealth sur toutes les pages existantes
    for page in context.pages:
        if HAS_STEALTH_SYNC:
            stealth_sync(page)
        else:
            page.add_init_script(STEALTH_JS)

    return context, p

def new_page(context):
    """Crée une nouvelle page avec stealth appliqué"""
    page = context.new_page()
    if HAS_STEALTH_SYNC:
        stealth_sync(page)
    else:
        page.add_init_script(STEALTH_JS)
    return page

# -----------------------------
# Exemple d'utilisation
# -----------------------------

if __name__ == "__main__":
    browser, p = launch_browser()
    page = new_page(browser)
    time.sleep(2)

    page.goto("https://bot.sannysoft.com")
    human_scroll(page)
    human_click(page, "body")

    input("👉 Appuie sur Entrée pour fermer...")
    browser.close()
    p.stop()
