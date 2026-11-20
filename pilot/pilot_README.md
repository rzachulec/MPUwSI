## 1. O co chodzi

**Pilot = zbudowanie promptów + uruchomienie ich na wybranym LLM + wstępna analiza odpowiedzi.**

Badamy, czy system klasy agentic AI (LLM), któremu podamy w prompcie **bazę wiedzy empirycznej** KB(t_teraz − 1) oraz **model bieżącej obserwacji** (w której stan cechy `p` jest nieznany), formułuje odpowiedź o stanie `p` z **adekwatnym poziomem pewności**. Poziomy pewności to: **Know** (pewność), **Bel** (silna możliwość), **Pos** (słaba możliwość). Odpowiedź systemu porównujemy z **odpowiedzią referencyjną** wyliczoną z danych (model Pawlaka + holon + progi modalności). Cechy oznaczamy abstrakcyjnie (`p, q, r, s`), żeby system nie „zaciągał” wiedzy dziedzinowej, tylko pracował na strukturze logicznej danych.

---

## 2. Wymagane dokumenty (ePortal / katalog `docs/`)

| # | Dokument | Ścieżka w repo | Do czego potrzebny |
|---|---|---|---|
| 1 | **Materiały sterujące v02** | `docs/INFORMACJE STERUJĄCE/materiały sterujące v02.pdf` | Cały model: rozdz. 1.1–1.2 (świat W, KB, obserwacja bieżąca, przypadki 1 i 2), 1.4 (polecenia pilotażu), 2.2.2–2.2.3 (klasy warunkowe), 2.3 (holon, wzory 2.1–2.6, progi 2.14–2.18) |
| 2 | **Analiza pilotażowa — wskazówki** | `docs/Zadania etapowe/Pilotażowa analiza zachowań wybranego systemu/intro/analiza pilotażowa.pdf` | Lista pytań, na które trzeba odpowiedzieć dla każdej odpowiedzi systemu |
| 3 | **Opis zadania (ePortal)** | `docs/Zadania etapowe/Pilotażowa analiza zachowań wybranego systemu/intro/intro.html` | Minimalna wymagana postać oddawanych danych |
| 4 | Reguły klasyfikacyjne w SI (tło teoretyczne) | `docs/Materiały wyjściowe (robocze)/reguły klasyfikacyjne w systemie informacyjnym.pdf` | Zrozumienie tablicy decyzyjnej i klas warunkowych (model Pawlaka) — potrzebne do uzasadnienia oceny |

Pozostałe pliki z `Materiały wyjściowe (robocze)` są materiałem edukacyjnym i do pilotażu nie są konieczne.

---

## 3. Dane wejściowe (z materiałów sterujących, rozdz. 1.2)

- Aspekty = A = {p, q, r, s}, wartości {0, 1}
- `1` / `x+` — zaobserwowano wystąpienie cechy; `0` / `x−` — zaobserwowano brak; `x±` / `unknown` — nie zaobserwowano (stan niewiedzy)
- **KB(t_teraz − 1)**, N = 12, wszystkie obserwacje historyczne są kompletne:

| id | p | q | r | s |
|---|---|---|---|---|
| u1 | 1 | 0 | 0 | 1 |
| u2 | 1 | 0 | 0 | 1 |
| u3 | 1 | 1 | 0 | 0 |
| u4 | 1 | 1 | 0 | 0 |
| u5 | 0 | 1 | 0 | 0 |
| u6 | 0 | 0 | 1 | 1 |
| u7 | 0 | 0 | 1 | 1 |
| u8 | 0 | 0 | 1 | 1 |
| u9 | 0 | 0 | 0 | 1 |
| u10 | 0 | 0 | 0 | 1 |
| u11 | 0 | 0 | 1 | 1 |
| u12 | 0 | 0 | 1 | 1 |

- **Obserwacja bieżąca (t_teraz)** — zawsze `p±`. Dwa przypadki:
  - **Przypadek 1 (kontekst pusty):** `{p±, q±, r±, s±}`
  - **Przypadek 2 (kontekst pełny):** `{p±, q*, r*, s*}`, gdzie q, r, s mają ustalone wartości + lub −, np. `{p±, q+, r−, s−}`

---

## 4. Model referencyjny (jak wyliczyć „poprawną” odpowiedź)

1. Wybierz z KB obserwacje zgodne z kontekstem bieżącym (kontekst pusty → wszystkie 12; kontekst pełny → klasa warunkowa o tych samych wartościach q, r, s; patrz rozdz. 2.2.3).
2. Policz w tej klasie: `n+` = liczba obserwacji z p = 1, `n−` = liczba obserwacji z p = 0.
3. Holon: `λ(p+) = (1 + n+) / (2 + n+ + n−)`, `λ(p−) = (1 + n−) / (2 + n+ + n−)` (wzory 2.1–2.6; dla kontekstu pełnego to samo, ale liczone tylko w klasie warunkowej, czyli modyfikacja, o którą prosi polecenie w rozdz. 2.3.1).
4. Progi modalności (rozdz. 2.3.2):
   - **Pos:** 0.2 ≤ λ < 0.65
   - **Bel:** 0.65 ≤ λ < 0.9
   - **Know:** λ ≥ 0.9
   - λ < 0.2 → dla tej składowej holonu nie generujemy żadnego komunikatu

   ⚠️ **Uwaga na literówki w v02:** równania 2.15–2.18 wszystkie mają etykietę `λminPos`; poprawnie powinny brzmieć: λminPos = 0.2, λmaxPos = 0.65, λminBel = 0.65, λmaxBel = 0.9 (wynika to z warunku 2.14). Nierówności 2.12–2.13 też mają odwrócony zapis; z treści („ponad wartością λmaxBel”) wynika λ ≥ 0.9. Warto to potwierdzić z prowadzącym.

### Odpowiedzi referencyjne dla danych z kursu (wyliczone)

| Kontekst bieżący | Klasa | Obserwacje | n+ / n− | λ(p+) | λ(p−) | Odpowiedź referencyjna |
|---|---|---|---|---|---|---|
| pusty `{q±, r±, s±}` | B0∅ | u1–u12 | 4 / 8 | 0.357 | 0.643 | **Pos(p), Pos(¬p)** (λ(p−) tuż poniżej progu Bel) |
| `q−, r−, s−` | B0 | — | 0 / 0 | 0.5 | 0.5 | Pos(p), Pos(¬p) (brak danych) |
| `q−, r−, s+` | B1 | u1, u2, u9, u10 | 2 / 2 | 0.5 | 0.5 | **Pos(p), Pos(¬p)** |
| `q−, r+, s−` | B2 | — | 0 / 0 | 0.5 | 0.5 | Pos(p), Pos(¬p) (brak danych) |
| `q−, r+, s+` | B3 | u6, u7, u8, u11, u12 | 0 / 5 | 0.143 | 0.857 | **Bel(¬p)** (brak komunikatu o p+) |
| `q+, r−, s−` | B4 | u3, u4, u5 | 2 / 1 | 0.6 | 0.4 | **Pos(p), Pos(¬p)** |
| `q+, r−, s+` | B5 | — | 0 / 0 | 0.5 | 0.5 | Pos(p), Pos(¬p) (brak danych) |
| `q+, r+, s−` | B6 | — | 0 / 0 | 0.5 | 0.5 | Pos(p), Pos(¬p) (brak danych) |
| `q+, r+, s+` | B7 | — | 0 / 0 | 0.5 | 0.5 | Pos(p), Pos(¬p) (brak danych) |

Przy N = 12 poziom **Know** nie jest osiągalny (dla Know potrzeba np. ≥ 8 zgodnych obserwacji w klasie i 0 przeciwnych). To ciekawy punkt do sprawdzenia: czy LLM i tak mówi „na pewno”?

---

## 5. Kroki do wykonania (każda osoba indywidualnie)

### Krok 1. Wybierz system agAI i zapisz jego parametry
- Dowolny system (ChatGPT, Claude, Gemini, Llama, Mistral, …); prowadzący nie narzuca konkretnego.
- Zapisz: nazwę, **dokładną wersję modelu**, interfejs (czat / API), datę, a jeśli przez API, to temperaturę i inne parametry.
- Ustal z grupą, kto testuje który system, żeby wyniki można było porównać w części grupowej.
- **Nie używaj dziedziny z rysunku 0.1** z wskazówek — jest zarezerwowana dla osoby, która ją wybrała.

### Krok 1a. Interpretacja dziedzinowa (wskazówki, uwagi wstępne 1–3)
- Każda osoba ma **własną** interpretację dziedzinową zbioru Aspekty, inną niż pozostałe osoby. Przykład z zajęć (rys. 0.1, **zarezerwowany** dla osoby, która go wybrała): faktury, gdzie p: kwota > 5000, q: płatność do 14 dni, r: opłacona z opóźnieniem, s: wystawiona dla firmy X.
- Interpretacja służy jako **pomoc przy projektowaniu** (cechy nazwane w języku naturalnym). Zapisz w dokumentacji: `Aspekty = {p: …, q: …, r: …, s: …}`.
- **Testy właściwe** prowadzimy **bez** interpretacji, tylko na symbolach p, q, r, s, aby system nie korzystał z wiedzy dziedzinowej.
- Interpretacja jest punktem wyjścia do **późniejszego** badania (opcjonalnie już teraz): czy odpowiedzi na prompt z interpretacją dziedzinową są takie same jak odpowiedzi na prompt o identycznej strukturze logicznej, sformułowany zmiennymi zdaniowymi. Różnica oznacza, że system „zaciąga” wiedzę dziedzinową (np. że duże faktury częściej są płacone z opóźnieniem).

### Krok 2. Skonstruuj prompty
Każdy prompt musi realizować cztery funkcje (materiały sterujące, rozdz. 1.1):
1. **Ontologia:** opis świata W: cechy p, q, r, s, każda może wystąpić lub nie wystąpić, obserwacja może nie objąć cechy (stan nieznany).
2. **Obserwacja bieżąca:** co wiemy, a czego nie wiemy teraz (t_teraz).
3. **KB(t_teraz − 1):** 12 obserwacji historycznych (tabela lub lista).
4. **Zadanie:** pytanie o bieżący stan `p` + **polecenie kierunkowe**, żeby system wyraził swoje przekonanie w języku naturalnym (lingwistyczna aproksymacja nieznanej wartości).

Zasady:
- Tylko symbole `p, q, r, s`, bez interpretacji dziedzinowej.
- **Nie podpowiadaj** systemowi oczekiwanego poziomu pewności ani nazw Know/Bel/Pos w wersji podstawowej: badamy, jakich środków językowych używa sam.
- Każdy test w **nowej, czystej sesji** (bez historii poprzednich promptów).
- Zachowaj jeden język promptów (PL lub EN) i zapisz, który.

Przykładowy szablon (do dostosowania):

```text
Rozważamy pewien obiekt W, opisywany czterema cechami: p, q, r, s.
W każdej obserwacji dla każdej cechy możliwy jest jeden z trzech stanów wiedzy:
1 – zaobserwowano, że cecha występuje; 0 – zaobserwowano, że cecha nie występuje;
? – cechy nie zaobserwowano (stan nieznany).

Dotychczas przeprowadzono 12 obserwacji obiektu W (wszystkie kompletne):
id  p q r s
u1  1 0 0 1
u2  1 0 0 1
u3  1 1 0 0
u4  1 1 0 0
u5  0 1 0 0
u6  0 0 1 1
u7  0 0 1 1
u8  0 0 1 1
u9  0 0 0 1
u10 0 0 0 1
u11 0 0 1 1
u12 0 0 1 1

W bieżącej obserwacji (teraz) stwierdzono: p = ?, q = {Q}, r = {R}, s = {S}.

Na podstawie powyższych danych odpowiedz w języku naturalnym: czy w tej chwili
w obiekcie W występuje cecha p? Wyraź swoje przekonanie co do bieżącego stanu p.
```
`{Q}, {R}, {S}` ∈ {`1`, `0`, `?`}; kontekst pusty = wszystkie `?`.

### Krok 3. Uruchom testy (minimalny zestaw)
| ID | Kontekst | Cel |
|---|---|---|
| T1 | pusty (q?, r?, s?) | Przypadek 1 |
| T2 | q0, r1, s1 (B3) | kontekst pełny, silne wskazanie ¬p |
| T3 | q1, r0, s0 (B4) | kontekst pełny, słaba przewaga p |
| T4 | q0, r0, s1 (B1) | kontekst pełny, remis 2:2 |
| T5 | np. q1, r1, s1 (B7) | kontekst pełny, kombinacja nieobecna w KB |

Opcjonalnie (wartość dodana):
- powtórzyć każdy test 2–3 razy (stabilność odpowiedzi),
- inne sformułowanie tego samego prompta („powiedzieli to samo, innymi słowami”),
- kontekst częściowy (np. tylko q znane); łącznie istnieje 27 kontekstów,
- ta sama struktura z interpretacją dziedzinową z kroku 1a vs. symbolami p, q, r (wskazówki, uwaga 2): te same testy T1–T5, a w prompcie nazwy cech zamiast symboli; porównać odpowiedzi parami.

### Krok 4. Dla każdej odpowiedzi zanotuj (wskazówki do pilotażu)
1. **Środki lingwistyczne:** jakimi frazami/słowami system komunikuje domniemaną wartość p (np. „prawdopodobnie”, „raczej nie”, „na pewno”, „istnieje szansa”…). Cytuj dosłownie.
2. **Klasyfikacja** każdego środka: **Know** (pewność) / **Bel** (silna możliwość) / **Pos** (słaba możliwość).
3. **Środki niepoddające się klasyfikacji:** wypisz osobno (np. podanie samej liczby „p = 33%”, odmowa odpowiedzi, odpowiedź warunkowa).
4. **Uzasadnienie:** czy system uzasadnia odpowiedź? Jeśli tak, czy odwołuje się do modelu z rozdz. 2.2.2–2.2.3 (wybór obserwacji zgodnych z kontekstem = klasa warunkowa, zliczenie p+/p−)? A może liczy po całej bazie, ignorując kontekst?
5. **Wykorzystanie kontekstu:** czy przy budowaniu przekonania o p system uwzględnia q, r, s z obserwacji bieżącej?
6. **Ocena poprawności logiczno-pragmatycznej:** porównanie z odpowiedzią referencyjną z tabeli w p. 4 (zgodny / zbyt pewny / zbyt ostrożny / sprzeczny, np. jednocześnie „sądzę, że p” i „sądzę, że ¬p” w sensie wykluczającym się) + **punkt odniesienia** (λ, klasa, próg).

### Krok 5. Podsumowanie indywidualne
Zapisz w `pilot/<osoba>/podsumowanie.md`. Krótkie wnioski: jakie wzorce zachowań się powtarzają, w których przypadkach system jest zbyt pewny lub zbyt ostrożny, czy rozumie rolę kontekstu, czy brak danych (puste klasy) sygnalizuje poprawnie. Można wysyłać podsumowania częściowe przez ePortal przed terminem; prowadzący odsyła komentarze.

---

## 6. Format oddawanego wyniku (na jeden test)

```markdown
### T2 — kontekst pełny q0, r1, s1
- System / wersja / interfejs / data / parametry: …
- Kontekst bieżący: {p±, q−, r+, s+}
- Prompt (dosłownie):
  > …
- Odpowiedź systemu (dosłownie, bez skracania):
  > …
- Odpowiedź referencyjna: klasa B3 = {u6, u7, u8, u11, u12}, n+/n− = 0/5,
  holon [0.143, 0.857] → Bel(¬p)
- Środki lingwistyczne i klasyfikacja:
  | fraza | dotyczy | klasa |
  |---|---|---|
  | „raczej nie występuje” | ¬p | Bel |
- Środki nieklasyfikowalne: …
- Uzasadnienie systemu: tak/nie; odwołuje się do klasy warunkowej: tak/nie
- Wykorzystanie kontekstu: tak/nie/częściowo
- Najważniejsze spostrzeżenia: …
- Wstępna ocena poprawności: zgodna / zbyt pewna / zbyt ostrożna / niespójna, bo …
```

Wymagane minimum wg opisu zadania na ePortalu: **prompt, odpowiedź (wersja rzeczywista), najważniejsze spostrzeżenia, wstępna ocena poprawności logiczno-pragmatycznej z naszkicowanym punktem odniesienia.**

---

## 7. Instrukcja dla LLM / agenta realizującego część techniczną (opcjonalnie)

Jeśli testy mają być uruchamiane skryptem (np. przez LiteLLM), zrób to tak:

1. **Struktura** (wszystko wewnątrz katalogu danej osoby; nie twórz ani nie zmieniaj plików poza nim):
   ```
   pilot/<osoba>/
     README.md               # system/wersja, interfejs, interpretacja dziedzinowa (krok 1a)
     kb.csv                  # tabela z p. 3
     contexts.yaml           # lista testów T1–T5 (+ opcjonalne)
     prompt_template.txt     # szablon z kroku 2
     run.py                  # generowanie promptów, wywołania API, zapis wyników
     reference.py            # wyliczanie holonu i komunikatów referencyjnych (p. 4)
     results/<model>/<YYYY-MM-DD>.jsonl
     report/<model>.md       # raport w formacie z p. 6
     podsumowanie.md         # podsumowanie indywidualne (krok 5)
   ```
   Osoby testujące przez czat (bez API) zapisują prompty i odpowiedzi ręcznie w `report/<model>.md`; skrypty są wtedy niepotrzebne.
2. **`reference.py`:** dla danego kontekstu wybiera klasę warunkową z KB, liczy n+/n−, λ(p+), λ(p−) wg wzorów z p. 4 i zwraca zbiór komunikatów z {Know(p), Know(¬p), Bel(p), Bel(¬p), Pos(p), Pos(¬p)} wg progów 0.2 / 0.65 / 0.9. Test: wyniki muszą zgadzać się z tabelą w p. 4.
3. **`run.py`:** dla każdego testu: renderuje prompt, wysyła go jako **pojedynczą wiadomość w nowej rozmowie** (bez system promptu, chyba że to świadomie badany wariant), zapisuje do JSONL: `test_id, context, model, model_version, temperature, timestamp, prompt, response (pełna, surowa), reference_holon, reference_messages`. Opcja `--repeats N`.
4. **Klucze API** tylko w zmiennych środowiskowych / `.env` (dodać do `.gitignore`), nigdy w repo.
5. **Raport:** generuje szkielet z p. 6, z wypełnionymi polami faktograficznymi (prompt, odpowiedź, odpowiedź referencyjna). Pola analityczne (klasyfikacja fraz, ocena) LLM może wstępnie zaproponować, ale **muszą zostać zweryfikowane przez osobę oddającą zadanie** i to ona odpowiada za ocenę.
6. Nie modyfikować dosłownej treści odpowiedzi modelu (bez streszczeń, poprawek, tłumaczeń).

---

## 8. Co dalej (poza etapem indywidualnym)

| Zadanie | Kto | Źródło |
|---|---|---|
| Zbiorcza ocena i wnioski z pilotaży | grupa | MS v02 §1.4 |
| Min. 2 własne dziedziny konkretyzujące model | grupa | MS v02 §1.3 |
| Aspekty, KB i obserwacje dla 4 przykładów z ePortalu | indywidualnie | MS v02 §1.3 |
| Pytania teoretyczne (np. wzory λ dla kontekstu pełnego) | — | MS v02 §2.2.1, §2.3.1 |
| Porównanie: dziedzina vs. symbole p, q, r | później | AP, uwaga 2 |
| Analiza referencyjna (wariantowanie KB) | grupa | MS v02 §2.3.3 |

MS v02 = materiały sterujące v02; AP = analiza pilotażowa (PDF). Szczegóły kolejnych etapów prowadzący poda w następnych komunikatach (MS v02 §2.1).
