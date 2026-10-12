"""
Scraper module for DMI UniCT (L-31 Informatica)
Handles scraping of:
- Docenti list for Canale F-N from https://web.dmi.unict.it/corsi/l-31/docenti
- Avvisi docenti from https://web.dmi.unict.it/corsi/l-31/avvisi-docente
- Avvisi generali CdS from https://web.dmi.unict.it/corsi/l-31/avvisi
"""

import re
import ssl
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import html

# Unverified SSL context for UniCT domain certificate issues
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

BASE_URL = "https://web.dmi.unict.it"
DOCENTI_URL = f"{BASE_URL}/corsi/l-31/docenti"
AVVISI_DOCENTE_URL = f"{BASE_URL}/corsi/l-31/avvisi-docente"
AVVISI_CDS_URL = f"{BASE_URL}/corsi/l-31/avvisi"

# Known fallback professors for Canale F-N in case of network issues
DEFAULT_FN_PROFESSORS = {
    "Calvagna Andrea Mario": {
        "surname": "calvagna",
        "courses": ["1015912 - PROGRAMMAZIONE I E LABORATORIO F - N"],
        "fn_courses": ["1015912 - PROGRAMMAZIONE I E LABORATORIO F - N"],
        "url": "/corsi/l-31/docenti/andrea.calvagna"
    },
    "Farinella Giovanni Maria": {
        "surname": "farinella",
        "courses": ["1015912 - PROGRAMMAZIONE I E LABORATORIO F - N"],
        "fn_courses": ["1015912 - PROGRAMMAZIONE I E LABORATORIO F - N"],
        "url": "/corsi/l-31/docenti/giovanni.farinella"
    },
    "Spata Massimo Orazio": {
        "surname": "spata",
        "courses": ["1015938 - ARCHITETTURA DEGLI ELABORATORI E LABORATORIO F - N"],
        "fn_courses": ["1015938 - ARCHITETTURA DEGLI ELABORATORI E LABORATORIO F - N"],
        "url": "/corsi/l-31/docenti/massimo.spata"
    },
    "Cavallaro Claudia": {
        "surname": "cavallaro",
        "courses": ["9795525 - STRUTTURE DISCRETE F - N"],
        "fn_courses": ["9795525 - STRUTTURE DISCRETE F - N"],
        "url": "/corsi/l-31/docenti/claudia.cavallaro"
    },
    "Cutello Vincenzo": {
        "surname": "cutello",
        "courses": ["9795525 - STRUTTURE DISCRETE F - N"],
        "fn_courses": ["9795525 - STRUTTURE DISCRETE F - N"],
        "url": "/corsi/l-31/docenti/vincenzo.cutello"
    },
    "Naselli Ornella": {
        "surname": "naselli",
        "courses": ["1015123 - ELEMENTI DI ANALISI MATEMATICA 2 F - N"],
        "fn_courses": ["1015123 - ELEMENTI DI ANALISI MATEMATICA 2 F - N"],
        "url": "/corsi/l-31/docenti/ornella.naselli"
    },
    "Zappala' Giuseppe": {
        "surname": "zappala",
        "courses": ["9795526 - ALGEBRA LINEARE E GEOMETRIA F - N"],
        "fn_courses": ["9795526 - ALGEBRA LINEARE E GEOMETRIA F - N"],
        "url": "/corsi/l-31/docenti/giuseppe.zappala"
    }
}


def fetch_html(url: str, timeout: int = 15) -> Optional[str]:
    """Fetches HTML content from given URL with custom User-Agent and SSL bypass."""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7"
            }
        )
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[Scraper] Errore nel recupero di {url}: {e}")
        return None


def get_fn_professors(force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
    """
    Parses https://web.dmi.unict.it/corsi/l-31/docenti to find all teachers
    associated with Canale F-N courses. Falls back to DEFAULT_FN_PROFESSORS on error.
    """
    html_content = fetch_html(DOCENTI_URL)
    if not html_content:
        return DEFAULT_FN_PROFESSORS

    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table")
    if not table:
        return DEFAULT_FN_PROFESSORS

    fn_teachers = {}
    rows = table.find_all("tr")

    for row in rows:
        cols = row.find_all(["td", "th"])
        if len(cols) < 2:
            continue

        teacher_col = cols[0]
        courses_col = cols[1]

        teacher_name = teacher_col.get_text(strip=True)
        if not teacher_name or teacher_name.lower() in ["cognome e nome", "docente"]:
            continue

        teacher_link = teacher_col.find("a")
        teacher_href = teacher_link["href"] if teacher_link and "href" in teacher_link.attrs else ""

        courses_li = courses_col.find_all("li")
        if courses_li:
            courses = [li.get_text(strip=True) for li in courses_li if li.get_text(strip=True)]
        else:
            courses = [courses_col.get_text(strip=True)]

        fn_courses = []
        for c in courses:
            if re.search(r"\bF\s*-\s*N\b", c, re.IGNORECASE):
                fn_courses.append(c)

        if fn_courses:
            # Teacher has at least one F-N course
            # Surnames are the first word(s) in Italian academic lists
            surname = teacher_name.split()[0].lower().replace("'", "").replace("’", "")
            fn_teachers[teacher_name] = {
                "surname": surname,
                "courses": courses,
                "fn_courses": fn_courses,
                "url": teacher_href if teacher_href.startswith("http") else f"{BASE_URL}{teacher_href}"
            }

    if not fn_teachers:
        return DEFAULT_FN_PROFESSORS

    return fn_teachers


def extract_notice_cards(html_content: str, source_type: str = "docente") -> List[Dict[str, Any]]:
    """Extracts cards from avvisi-docente or avvisi (CdS) pages."""
    soup = BeautifulSoup(html_content, "html.parser")
    cards = soup.find_all("div", class_="card-wrapper")
    notices = []

    for c in cards:
        # Date
        date_el = c.find("span", class_="data")
        date_str = date_el.get_text(strip=True) if date_el else ""

        # Title & Link
        title_el = c.find("h5", class_="card-title")
        title_str = title_el.get_text(strip=True) if title_el else ""

        link_el = c.find("a", href=True)
        link_str = link_el["href"] if link_el else ""
        if link_str.startswith("/"):
            link_str = f"{BASE_URL}{link_str}"

        # Author / Signature
        sig_el = c.find("span", class_="card-signature")
        author_str = sig_el.get_text(strip=True) if sig_el else ""
        if not author_str and source_type == "cds":
            author_str = "CdS Informatica (L-31)"

        # Text snippet
        paragraphs = c.find_all("p")
        body_parts = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and not text.startswith("http"):
                body_parts.append(text)
        body_text = "\n".join(body_parts)

        # Unique notice ID (relative path or full url)
        notice_id = link_str.split("?")[0] if link_str else title_str

        notices.append({
            "id": notice_id,
            "title": html.unescape(title_str),
            "date": date_str,
            "link": link_str,
            "author": html.unescape(author_str),
            "body": html.unescape(body_text),
            "source_type": source_type
        })

    return notices


def is_notice_relevant_to_fn(
    notice: Dict[str, Any],
    fn_professors: Dict[str, Dict[str, Any]],
    include_cds_general: bool = False
) -> Dict[str, Any]:
    """
    Evaluates if a notice is relevant to Canale F-N students.
    Returns:
    {
        'is_relevant': bool,
        'reason': str,
        'matched_professor': Optional[str]
    }
    """
    title = notice.get("title", "")
    body = notice.get("body", "")
    author = notice.get("author", "")
    source_type = notice.get("source_type", "docente")
    combined_text = f"{title} {body}".strip()

    # 1. Check for explicit mention of Canale F-N in title or body
    fn_regex = r"\b(?:canale\s+F[-\s]*N|F\s*-\s*N|canale\s+F)\b"
    if re.search(fn_regex, combined_text, re.IGNORECASE):
        return {
            "is_relevant": True,
            "reason": "Menzione esplicita del Canale F-N nel testo o titolo",
            "matched_professor": author
        }

    # 2. Check if author is one of the Canale F-N professors
    # Clean author to extract surname
    author_clean = re.sub(r"^(?:Prof\.ssa|Prof\.)\s*", "", author, flags=re.IGNORECASE).strip()
    author_words = [w.strip(".,'’").lower() for w in author_clean.split()]

    matched_fn_teacher = None
    matched_teacher_name = None

    for prof_name, data in fn_professors.items():
        surname = data["surname"].lower()
        if surname in author_words or any(surname in w for w in author_words):
            matched_fn_teacher = data
            matched_teacher_name = prof_name
            break

    if matched_fn_teacher:
        # Check if notice is explicitly targeted ONLY to a different channel
        # e.g. "Canale AE", "Canale A-E", "[O-Z]", "Canale O-Z", "Canale M-Z"
        other_channel_regex = r"\b(?:canale\s*(?:A[-\s]*E|AE|O[-\s]*Z|OZ|M[-\s]*Z|MZ|A[-\s]*D))\b|\[O-Z\]|\[A-E\]"
        has_other_channel = bool(re.search(other_channel_regex, combined_text, re.IGNORECASE))
        has_fn_channel = bool(re.search(fn_regex, combined_text, re.IGNORECASE))

        if has_other_channel and not has_fn_channel:
            return {
                "is_relevant": False,
                "reason": "Docente F-N ma avviso riservato ad altro canale",
                "matched_professor": matched_teacher_name
            }

        fn_course_names = ", ".join(c.split("-")[-1].strip() for c in matched_fn_teacher.get("fn_courses", []))
        return {
            "is_relevant": True,
            "reason": f"Docente Canale F-N: {author_clean} ({fn_course_names})",
            "matched_professor": matched_teacher_name
        }

    # 3. If notice is from CdS (general degree announcements)
    if source_type == "cds":
        if include_cds_general:
            return {
                "is_relevant": True,
                "reason": "Avviso Generale CdS Informatica (L-31)",
                "matched_professor": "CdS Informatica"
            }

    return {
        "is_relevant": False,
        "reason": "Non correlato al Canale F-N",
        "matched_professor": None
    }


def fetch_all_fn_notices(
    max_pages: int = 2,
    include_cds_general: bool = False
) -> List[Dict[str, Any]]:
    """
    Scrapes and filters notices for Canale F-N from both avvisi-docente
    and optionally avvisi CdS.
    """
    fn_profs = get_fn_professors()
    all_notices = []

    # 1. Fetch avvisi docente
    for page in range(max_pages):
        page_param = f"?page={page}" if page > 0 else ""
        url = f"{AVVISI_DOCENTE_URL}{page_param}"
        html_page = fetch_html(url)
        if html_page:
            cards = extract_notice_cards(html_page, source_type="docente")
            all_notices.extend(cards)

    # 2. Fetch avvisi CdS if requested
    if include_cds_general:
        for page in range(max(1, max_pages // 2)):
            page_param = f"?page={page}" if page > 0 else ""
            url = f"{AVVISI_CDS_URL}{page_param}"
            html_page = fetch_html(url)
            if html_page:
                cards = extract_notice_cards(html_page, source_type="cds")
                all_notices.extend(cards)

    # 3. Filter relevant notices
    relevant_notices = []
    seen_ids = set()

    for n in all_notices:
        if n["id"] in seen_ids:
            continue
        seen_ids.add(n["id"])

        eval_res = is_notice_relevant_to_fn(n, fn_profs, include_cds_general=include_cds_general)
        if eval_res["is_relevant"]:
            n["reason"] = eval_res["reason"]
            n["matched_professor"] = eval_res["matched_professor"]
            relevant_notices.append(n)

    return relevant_notices
