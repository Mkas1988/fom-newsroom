# FOM Design System & UX Guidelines

Referenzdokument fuer alle FOM-Webprojekte. Basierend auf dem FOM Newsroom (2025/2026).

---

## 1. Farben

### Primaerfarben

| Token | Hex | Verwendung |
|-------|-----|------------|
| `--fom-teal` | `#00C6B2` | Primaerfarbe, Header-Hintergrund, Links, Buttons, Hover-Akzente |
| `--fom-teal-dark` | `#009F8F` | Hover-Zustand der Primaerfarbe, Tags |
| `--fom-teal-darker` | `#00776B` | Starker Kontrast |
| `--fom-teal-light` | `#E5F9F7` | Tag-Hintergund, leichte Akzente |
| `--fom-teal-100` | `#CCF3EF` | Subtile Hintergruende |
| `--fom-teal-200` | `#99E8E0` | — |
| `--fom-teal-300` | `#66DDD1` | — |
| `--fom-teal-400` | `#33D2C2` | — |

### Sekundaerfarben

| Token | Hex | Verwendung |
|-------|-----|------------|
| `--fom-blue` | `#0071DE` | Sekundaere Akzente |
| `--fom-blue-dark` | `#005AB2` | Hover-Zustand Blau |

### Neutrale Farben

| Token | Hex | Verwendung |
|-------|-----|------------|
| `--fom-black` | `#121212` | Text, dunkle Buttons |
| `--fom-white` | `#FFFFFF` | Hintergruende, Text auf dunklem Grund |
| `--fom-bg` | `#FFFFFF` | Seiten-Hintergrund |
| `--fom-bg-alt` | `#F2F0F0` / `#F7F7F7` | Alternativer Hintergrund (Hero, Sections) |
| `--fom-gray` | `#6D6D6D` | Sekundaerer Text, Platzhalter |
| `--fom-gray-light` | `#E6E6E6` | Borders, Trennlinien |
| `--fom-gray-dark` | `#4B4B4B` | Starker Sekundaertext |
| `--fom-gray-800` | `#303030` | — |
| `--fom-text` | `#121212` / `#202020` | Standard-Textfarbe |
| `--fom-text-light` | `#6D6D6D` | Sekundaerer Text |

### Statusfarben

| Token | Hex | Verwendung |
|-------|-----|------------|
| `--fom-error` | `#E81818` | Fehlermeldungen |
| `--fom-success` | `#77B502` | Erfolgsmeldungen |
| `--fom-warning` | `#F2C91B` | Warnungen |

### Spezialfarben

| Verwendung | Hex |
|------------|-----|
| Footer-Hintergrund | `#0B2623` (dunkles Gruen) |
| Footer-Text | `rgba(255,255,255,.85)` |
| Footer-Ueberschriften | `rgba(255,255,255,.4)` |
| Footer-Links | `rgba(255,255,255,.75)` |
| Footer-Copyright | `rgba(255,255,255,.4)` |

---

## 2. Typografie

### Schriftfamilien

| Zweck | Schriftart | Fallback |
|-------|-----------|----------|
| Ueberschriften | `Neue-Haas-Grotesk-Display-Pro` | Helvetica, Arial, sans-serif |
| Fliesstext | `Neue-Haas-Grotesk-Text-Pro` | Helvetica, Arial, sans-serif |
| Logo-Wortmarke | `NHaasGroteskDSPro-65Md` | — |

### Font-Dateien (woff2/woff)

```
fonts/Neue-Haas-Grotesk-Text-Pro/
  Neue-Haas-Grotesk-Text-Pro-55-Regular.woff2  (400)
  Neue-Haas-Grotesk-Text-Pro-75-Bold.woff2     (700)

fonts/Neue-Haas-Grotesk-Display-Pro/
  Neue-Haas-Grotesk-Display-Pro-75-Bold.woff2   (700)
```

### Schriftgroessen

| Element | Groesse | Gewicht | Besonderheiten |
|---------|---------|---------|----------------|
| H1 (Slide-Titel) | 36px | 700 | Display-Pro, letter-spacing: -0.3px |
| H1 (Artikel) | 36px | 700 | Display-Pro, line-height: 1.2 |
| H2 (Section Title) | 32px | 700 | Display-Pro, letter-spacing: -0.3px |
| H3 (Card Title) | 20px | 700 | Display-Pro, line-height: 1.3 |
| Body Text | 16px | 400 | Text-Pro, line-height: 1.6 |
| Artikel Body | 18px | 400 | line-height: 1.9 |
| Excerpt | 15-16px | 400 | line-height: 1.6-1.7 |
| Meta Text | 13-14px | 400-600 | — |
| Tags | 12px | 600-700 | uppercase, letter-spacing: 0.8px |
| Navigation | 15px | 500 | — |
| Header Title | 26px | 700 | Display-Pro, scrolled: 20px |
| Header Subtitle | 11.5px | 400 | rgba(255,255,255,.7) |
| Footer Text | 14px | 400 | line-height: 1.8 |
| Footer Ueberschriften | 13px | 700 | uppercase, letter-spacing: 1.2px |

### Textrendering

```css
-webkit-font-smoothing: antialiased;
```

---

## 3. Spacing & Layout

### Globaler Radius

```css
--radius: 8px;   /* index.html (Cards) */
--radius: 12px;  /* artikel.html, kontakt.html (groessere Elemente) */
```

### Content-Container

| Bereich | Max-Width | Padding |
|---------|-----------|---------|
| Header | 100% | 0 48px |
| Content | 1200px | 0 32px |
| Hero Slider | 1400px | 20px 32px 0 |
| Search/Filter | 1400px | 28px 32px 0 |
| Footer | 1200px | 64px 32px 32px |
| Artikel Body | 800px | 0 32px |

### Grid-Systeme

```css
/* News Grid (3 Spalten) */
.news-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 28px;
}

/* Footer Grid */
.footer-inner {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    gap: 48px;
}
```

### Standard-Abstande

| Kontext | Wert |
|---------|------|
| Section margin-top | 48px |
| Section margin-bottom (Footer) | 100px |
| Card Padding | 28px |
| Card Gap | 28px |
| Filter Chips Gap | 8px |
| Tag Gap | 6px |
| Meta Gap | 12-16px |

---

## 4. Komponenten

### 4.1 Header (Sticky, 2 States)

**Default State:**
- Hoehe: 96px
- Background: `--fom-teal`
- Logo zentriert (absolute, 50%/50%)
- Logo-Hoehe: 60px (Header), 120px (Footer)
- Links: FOM Newsroom + Subtitle
- Rechts: Suche-Icon, Nav-Links, Hamburger (mobil)

**Scrolled State (compact):**
- Hoehe: 56px
- Logo ausgeblendet (opacity: 0)
- Subtitle ausgeblendet
- Titel: 20px

```css
header { position: sticky; top: 0; z-index: 100; transition: all .3s ease; }
header.scrolled .header-inner { height: 56px; }
header.scrolled .logo-center { opacity: 0; pointer-events: none; }
```

### 4.2 Cards

**Struktur:**
```
.card
  .card-image-wrap > img.card-image
  .card-body
    .card-meta > .card-date
    .card-tags > .card-tag (x n)
    .card-title > a
    .card-excerpt
    .card-footer > .card-link
```

**Styling:**
- Border: `1px solid var(--fom-gray-light)`
- Border-Radius: `var(--radius)` (8px)
- Image: height 200px, object-fit: cover
- Hover: border-color teal, shadow `0 8px 32px rgba(90,185,167,.1)`, translateY(-3px)
- Image Hover: scale(1.04)
- Gesamte Karte klickbar (Link auf Bild + Text)

**Tags auf Cards:**
- margin-top: 6px, margin-bottom: 12px
- Tag: 12px, font-weight 600, teal-dark auf teal-light Background
- Padding: 4px 12px, border-radius: 14px

**Card Link (CTA):**
- Teal, 13px, 700
- Border: 1.5px solid teal, border-radius: 20px
- Padding: 8px 20px
- Hover: background teal, color white
- Pfeil via `::after { content: ' →'; }`

### 4.3 Hero Slider

- Aspect Ratio: 16 / 7
- Border-Radius: 16px
- Overlay: linear-gradient (schwarz von unten)
- Transition: opacity .8s ease (Crossfade)
- Auto-Play: 6 Sekunden
- Dots: 10px Kreis, active = 28px Pille in Teal
- Pause-Button: 44px, border-radius: 10px, backdrop-filter: blur(8px)
- Inhalt: Tag (Border-Pill), Datum, Titel, Excerpt (2 Zeilen max)

### 4.4 Search & Filter

**Suchleiste:**
- Border: 1px solid gray-light, border-radius: 16px
- Input: 20px 28px Padding, 16px font
- Submit-Button: 56x56px, border-radius: 12px, schwarz
- Focus: box-shadow `0 4px 24px rgba(0,0,0,.06)`

**Filter Chips:**
- Padding: 7px 16px
- Border: 1.5px solid gray-light, border-radius: 8px
- Active: Background schwarz, Text weiss

### 4.5 Artikel-Seite

**Hero Section:**
- Background: `--fom-bg-alt`
- Padding: 40px 32px 48px
- Breadcrumb > Tags > Meta (Datum + Lesezeit) > H1 > Summary > Share-Bar

**Lesezeit-Berechnung:**
```javascript
const readingMinutes = Math.max(1, Math.round(wordCount / 200));
// Anzeige: "X Min. Lesezeit"
```

**Body:**
- Max-Width: 800px
- Schrift: 18px, line-height: 1.9
- Absaetze: margin-bottom 1.5em
- Bilder: max-width 100%, border-radius: var(--radius)

**Boilerplate-Box:**
- Background: `--fom-bg-alt`
- Border: 1px solid gray-light
- Border-Radius: 16px
- Padding: 32px 36px
- Link "Mehr erfahren auf fom.de" rechts unten

### 4.6 Galerie-Komponenten (im Artikel)

**4 Styles:**

1. **Mosaik (Standard):** Hero-Bild gross + 2-4 kleinere daneben, border-radius: 12px
2. **Slider/Karussell:** Horizontales Scrollen mit Navigation, Dots, Counter
3. **Raster (Grid):** Gleichmaessige Kacheln (2-4 Spalten), gap: 8px
4. **Masonry:** Pinterest-artiges Layout mit CSS columns

**Lightbox:**
- Background: rgba(0,0,0,.92), backdrop-filter: blur(12px)
- Bild: max-height 85vh, border-radius: 12px
- Thumbnail-Strip am unteren Rand
- Navigation: Pfeile links/rechts, Counter oben
- Keyboard: Escape, Pfeil-Links/Rechts

**Galerie-Editor:**
- Bilder per Drag & Drop oder URL hinzufuegen
- Bilder aus Mediencenter waehlen (Toggle-Selection)
- Style-Picker mit visuellen Icons
- Spaltenauswahl (2-4 Spalten)
- Caption-Felder pro Bild

### 4.7 Footer (Dark Theme)

**Struktur:**
```
footer (#0b2623)
  .footer-logo > img (120px, margin-left: -30px fuer SVG-Whitespace)
  .footer-inner (Grid 2fr 1fr 1fr 1fr)
    .footer-about > p (Markentext)
    .footer-links "Newsroom" (News, Mediencenter, Kontakt)
    .footer-links "FOM Hochschule" (Studiengaenge, Standorte, Forschung, fom.de)
    .footer-links "Kontakt" (Pressestelle, Telefon, E-Mail)
  .footer-accreditation (Qualitaetslogos: FIBAA, AACSB, Systemakkreditierung)
  .footer-bottom (Copyright + Impressum/Datenschutz)
```

**Logo:** Negativ-Variante (weiss auf transparent), SVG mit Wortmarke

### 4.8 Modals / Overlays

- Background: rgba(0,0,0,.4), backdrop-filter: blur(4px)
- Panel: weiss, border-radius: 20px
- Max-Width: 680px (Admin) / 520px (Formulare)
- Shadow: `0 24px 80px rgba(0,0,0,.15)`
- Close-Button: 36x36px, border-radius: 10px, oben rechts
- Header: border-bottom 1px solid gray-light

### 4.9 Buttons

**Primaer (Teal):**
```css
background: var(--fom-teal);
color: white;
border-radius: 10px;
padding: 10px 24px;
font-weight: 600;
/* Hover: */ background: var(--fom-teal-dark);
```

**Sekundaer:**
```css
background: white;
border: 1px solid var(--fom-gray-light);
color: var(--fom-text);
/* Hover: */ background: var(--fom-bg-alt);
```

**Pill-Button (CTA auf Cards):**
```css
border: 1.5px solid var(--fom-teal);
border-radius: 20px;
padding: 8px 20px;
/* Hover: */ background: var(--fom-teal); color: white;
```

**Danger:**
```css
/* Hover: */ border-color: #ef4444; color: #ef4444;
```

### 4.10 Tags / Chips

**Artikel-Tags:**
```css
font-size: 12px;
font-weight: 600;
color: var(--fom-teal-dark);
background: var(--fom-teal-light);
padding: 4px 12px;
border-radius: 14px;
```

**Filter-Chips:**
```css
padding: 7px 16px;
border: 1.5px solid var(--fom-gray-light);
border-radius: 8px;
/* Active: */ background: var(--fom-black); color: white;
```

### 4.11 FAB (Floating Action Button)

```css
position: fixed;
bottom: 28px;
right: 28px;
width: 52px;
height: 52px;
border-radius: 14px;
background: var(--fom-teal);
box-shadow: 0 4px 20px rgba(0, 198, 178, .3);
z-index: 200;
```

---

## 5. Animationen & Transitions

| Element | Eigenschaft | Dauer | Easing |
|---------|------------|-------|--------|
| Header Hoehe | height | .3s | ease |
| Header Logo | opacity | .3s | ease |
| Card Hover | border, shadow, transform | .25s | default |
| Card Image | transform (scale) | .4s | default |
| Slider Crossfade | opacity | .8s | ease |
| Navigation Links | all | .2s | default |
| Buttons | all | .15s | default |
| Mobile Menu | transform | .35s | cubic-bezier(.4,0,.2,1) |
| Backdrop | opacity | .3s | ease |

---

## 6. Responsive Breakpoints

| Breakpoint | Aenderungen |
|------------|-------------|
| `<= 1024px` | News-Grid: 2 Spalten, Footer: 2 Spalten |
| `<= 768px` | Header: 64px/52px, Logo-Center hidden, Hamburger sichtbar, News-Grid: 1 Spalte, Footer: 1 Spalte, Slide-Titel: 24px |
| `<= 480px` | Card-Body Padding: 20px, Header Padding: 0 16px |

### Mobile Menu (Slide-in von rechts)

```css
width: 420px;
max-width: 85vw;
transform: translateX(100%);  /* closed */
transform: translateX(0);     /* open */
transition: transform .35s cubic-bezier(.4, 0, .2, 1);
```

---

## 7. Icons

Alle Icons sind inline SVGs (kein Icon-Font):
- Stroke-basiert: stroke-width 2, stroke-linecap round, stroke-linejoin round
- Groesse: 20px (Header), 16px (Buttons), 18px (Slider)
- Farbe: currentColor oder white

Verwendete Icons:
- Suche (Lupe)
- Schliessen (X)
- Hamburger (3 Linien)
- Chevron (rechts)
- Teilen (Share)
- Download
- Zahnrad (Settings/Admin)
- Pause/Play
- Pfeil links/rechts
- Personen (Experten-Service)

---

## 8. Logo-Varianten

### Header (Farbig)
- `fom-logo.svg` – Teal/Weiss auf transparentem Hintergrund
- Hoehe: 60px (Header-Center)

### Footer (Negativ)
- `fom-logo-white.svg` – Weisse Schrift, teal Quadrat (#00998B)
- Hoehe: 120px
- `margin-left: -30px` (SVG hat internen Whitespace links)

### Wortmarke
- "Die Hochschule. Fuer Berufstaetige." rechts neben dem FOM-Quadrat

---

## 9. Schatten

| Kontext | Box-Shadow |
|---------|-----------|
| Card Hover | `0 8px 32px rgba(90, 185, 167, .1)` |
| Search Focus | `0 4px 24px rgba(0, 0, 0, .06)` |
| Modal | `0 24px 80px rgba(0, 0, 0, .15)` |
| FAB | `0 4px 20px rgba(0, 198, 178, .3)` |
| Header Search | `0 4px 20px rgba(0, 0, 0, .06)` |

---

## 10. Markentext (Boilerplate)

> Mit rund 45.000 Studierenden zaehlt die gemeinnuetzige FOM zu den groessten Hochschulen Europas. Initiiert durch die gemeinnuetzige Stiftung fuer internationale Bildung und Wissenschaft ermoeglicht sie Berufstaetigen, Auszubildenden, Abiturienten und international Studierenden ein Hochschulstudium. Die FOM ist staatlich anerkannt und bietet mehr als 60 akkreditierte Bachelor- und Master-Studiengaenge an – im Campus-Studium+ an bundesweit ueber 30 Hochschulzentren oder im einzigartigen Digitalen Live-Studium aus den FOM Studios. Studierende koennen zudem mit den FOM Auslandsprogrammen weltweit Studienerfahrungen an renommierten Partnerhochschulen sammeln.

---

## 11. UX-Prinzipien

### Navigation
- Sticky Header mit Kompakt-Modus beim Scrollen
- Mobile: Slide-in Menu von rechts (nicht Dropdown)
- Breadcrumb auf Unterseiten: `Newsroom / {Kategorie}`
- Suche: Overlay ueber gesamte Breite

### Inhalte
- Hero-Slider mit Auto-Play (6s) und Pause-Button
- Cards: Gesamte Karte klickbar (Bild + Text)
- Tags prominent vor der Headline platzieren
- Lesezeit-Angabe bei Artikeln
- Verwandte Artikel am Ende (tag-basiert)

### Formulare
- Modal-basiert (nicht eigene Seite)
- Mailto-Integration fuer Anfragen
- Klare Labels und Pflichtfeld-Markierung

### Bearbeitungsmodus
- Toggle ueber Settings-FAB
- contentEditable fuer Artikel-Body
- Galerie-Insert per Marker zwischen Absaetzen
- Aenderungen in localStorage gespeichert
- Unsaved-Changes-Indikator (roter Dot)
- Zuruecksetzen-Funktion

### Performance
- font-display: swap fuer alle Webfonts
- Lazy Loading fuer Bilder (IntersectionObserver bei Slider)
- Keine externen CSS/JS-Frameworks
- Alles vanilla HTML/CSS/JS

### Barrierefreiheit
- Semantisches HTML (header, nav, main, footer, article)
- Alt-Texte auf Bildern
- Keyboard-Navigation in Lightbox (Escape, Pfeiltasten)
- Ausreichende Farbkontraste

---

## 12. API-Integration (MyNewsdesk)

```
Base URL: https://www.mynewsdesk.com/services/pressroom
API Key: 2J8377Ow95pCNFI_DPzZTQ

Endpoints:
- /list/{key}?format=json&type_of_media={type}&limit={n}
- /view/{key}?format=json&item_id={id}
- /search/{key}?format=json&query={q}&type_of_media={type}

Typen: pressrelease (→ "News"), image, video, document, contact_person
```

### Datumsformat (deutsch)

```javascript
const MONTHS = ['Januar','Februar','Maerz','April','Mai','Juni',
                'Juli','August','September','Oktober','November','Dezember'];
// Ausgabe: "18. Dezember 2025"
```

---

## 13. Dateistruktur

```
fom-newsroom/
├── index.html          (Startseite mit Slider, News-Grid, Admin)
├── artikel.html        (Artikel-Detail mit Editor, Galerien)
├── medien.html         (Mediencenter mit Kategorie-Filter)
├── kontakt.html        (Presseteam, Experten-Service, Formulare)
├── autor.html          (Autoren-Profil)
├── robots.txt
├── fom-logo.svg        (Farbig)
├── fom-logo-white.svg  (Negativ/Footer)
└── fonts/
    ├── Neue-Haas-Grotesk-Text-Pro/
    └── Neue-Haas-Grotesk-Display-Pro/
```
