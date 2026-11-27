# Zagregowana ocena jakościowa pilotaży

*Wersja robocza przygotowana z pomocą LLM na podstawie pilotaży indywidualnych; do weryfikacji przez grupę.*

Polecenie grupowe 1 z MS v02 §1.4: „Opracować zagregowaną ocenę jakościową i wnioski z pilotażowych badań indywidualnych”.

## 1. Zakres i materiał

W pilotażach przebadano siedem systemów agAI – od otwartego modelu 11B po duże systemy komercyjne. Testy obejmowały kontekst pusty, pełny i częściowy, klasy jednomyślne, remisy i kombinacje nieobecne w bazie, a w części przypadków także wariant z interpretacją dziedzinową.

| System (interfejs) | KB | Pytanie o | Zakres testów |
|---|---|---|---|
| Bielik-11B-v3.1, Qwen3.6-35B-A3B, Qwen3.5-122B-A10B (API, temperature 0.7) | kursowa, N = 12 | p | T1–T5 ×3, wariant dziedzinowy D1–D5 ×3, siatka 27 kontekstów ×1 (57 odpowiedzi na model) |
| Claude Opus 5.5 (osobne instancje) | 5 obserwacji h1–h5 | r | test 1 ×3, testy 2 i 3 ×1 |
| Codex | 12 obserwacji | p | 5 prób |
| Gemini (czat) | kursowa, N = 12 | p | T1–T5 |
| gpt-6-luna, tryb rozumowania medium (Codex) | 15 rekordów z UCI *Bank Marketing*, zakodowanych jako p, q, r, s | p, q, r, s | 6 scenariuszy A–F ×3, odpowiedź w JSON |

## 2. Wspólny punkt odniesienia

Odpowiedzi oceniano względem jednego modelu: wybór klasy warunkowej (cała KB dla kontekstu pustego, obserwacje o identycznych wartościach znanych cech dla kontekstu pełnego), zliczenie n⁺ i n⁻, holon λ = (1 + n)/(2 + n⁺ + n⁻) i progi Pos [0,2; 0,65), Bel [0,65; 0,9), Know ≥ 0,9, przy odczytaniu wzorów 2.12–2.18 opisanym w `pilot_README.md` §4. Dla pustej klasy wzór daje parę (0,5; 0,5), czyli Pos(p) i Pos(¬p).

## 3. Wzorce zbieżne

**3.1. Silne systemy wybierają klasę warunkową poprawnie.** Tam, gdzie klasa jest niepusta, Claude, Codex, Gemini i oba Qwen zwykle wskazują dokładnie właściwe obserwacje i poprawnie je liczą: Codex wymienia u2, u8, u11 w próbie 3 i u4, u6 w próbie 4, Gemini wylicza B3, B4 i B1 wiersz po wierszu (T2–T4), Claude trafia w klasę {h2, h3} (test 1), a oba Qwen robią to w 11 z 12 odpowiedzi T2–T5. Słabiej wypada gpt-6-luna: w 4 z 12 prób z kontekstem (D2, D3, E2, F1) policzył częstości z całej historii, a w E2 i F1 doprowadziło to do wskazania przeciwnego niż wynika z klasy. Bielik nie wyznaczył klasy ani razu (0/12) i służy jako dolny punkt odniesienia.

**3.2. Słabsza wartość znika z odpowiedzi.** Model referencyjny często wymaga dwóch komunikatów naraz. Systemy prawie zawsze podają jeden. Codex w próbie 1 pisze „Bieżący stan p+ wydaje się bardziej prawdopodobny, choć pewność jest ograniczona”, a w próbie 3 „Raczej p−” – o drugiej wartości w obu przypadkach milczy. Claude zostawia ¬r w formie negacji pewności: „sądzę, że r raczej zachodzi, ale nie mam co do tego pewności” (test 2). Gemini w T3 przedstawia brak p wyłącznie w zestawieniu liczbowym. Przy gpt-6-luna ten sam efekt widać mimo formatu JSON, który pozwalał podać kilka pozycji na cechę: „Gdy punkt odniesienia dopuszcza oba komunikaty, model pomijał drugą wartość”. Wyjątki istnieją, ale są rzadkie – Claude w przebiegach 2 i 3 testu 1 napisał wprost „nie można wykluczyć r−”, a Gemini w T1 sformułował jawne Pos dla słabszej wartości („jej obecności nie można całkowicie wykluczyć”), zostawiając za to niejednoznaczną siłę dominującego ¬p. Negacja pewności („nie mam pewności”, „brak jest pewności”) to zresztą najczęstszy środek asekuracji we wszystkich systemach, a według przyjętych kryteriów nie da się jej zaklasyfikować.

**3.3. Surowa częstość zamiast holonu.** Żaden system nie „wygładza” zliczeń. Claude podaje „około 80%” tam, gdzie λ = 5/7 (test 2), gpt-6-luna podaje 3/4 przy referencyjnym 2/3 (scenariusz C), a Gemini w T3 przenosi 2/3 na „Cecha p prawdopodobnie występuje w obiekcie W”, czyli Bel(p), choć λ(p⁺) = 3/5 mieści się w Pos. Przy dużych klasach różnica jest bez znaczenia. Przy klasach dwu- czy trzyelementowych decyduje o przesunięciu z Pos do Bel.

**3.4. Remis: zachowanie zależy od modelu, nie od rodziny.** Codex przy 1:1 pozostał neutralny („żadna z możliwości nie ma wyraźniejszego poparcia”, próba 4), podobnie Gemini przy 2:2 („tyle samo przemawia za jej wystąpieniem, co za jej brakiem”, T4). Claude przeciwnie – rozpoznał remis w {h2, h3}, po czym rozstrzygnął go częstościami spoza klasy („Ogólnie r zachodziło w 4 z 5 obserwacji”), i to we wszystkich trzech przebiegach w tym samym kierunku. Qwen3.5 w T4#1 doszedł do „istnieje silne prawdopodobieństwo, że cecha p nie występuje (stan 0)”, a Qwen3.6 rozstrzygał remis w 3 z 9 przypadków, sięgając po rozkład 8/12 z całej KB albo naiwnego Bayesa. Nawet neutralna odpowiedź bywa przy tym zbyt dosłowna: „szanse wynoszą dokładnie 50 na 50” (Gemini) przenosi proporcję z czterech obserwacji na stan bieżący.

**3.5. Jednomyślna klasa przy małym N prowokuje Know.** Referencja przy N = 12 nigdy nie daje Know, a jednak Qwen3.6 przy klasie B3 (0/5) napisał „bliskie pewności” (T2#2) i „bardzo silne i pewne” ze „100% zgodności z danymi historycznymi” (T2#3), a Gemini zakończył T2 zdaniem „Wszystkie dostępne dane jednoznacznie wskazują, że w bieżącej obserwacji cecha p nie występuje”. Qwen3.5 w T2 trzy razy trafił w Bel(¬p), ale w wariancie dziedzinowym, po zgubieniu u5, też doszedł do „100%” (D3#2, D3#3). Inaczej Codex i Claude: żaden z nich nie użył Know, a Codex sam zauważył, że „sześć zgodnych przypadków nie daje pewności” (próba 2). Podobną intuicję widać w Qwen3.5 T2#3: „prawdopodobnie 0, ale nieznane”. Fraza „z dużą pewnością” u gpt-6-luna (A2, B3) została zaklasyfikowana jako Bel.

**3.6. Pusta klasa – najwyraźniejsza rozbieżność z modelem.** Tu zbieżność jest największa i zarazem najbardziej niekorzystna. Mechanizm powtarza się w czterech systemach: system zauważa, że kombinacji nie było w KB, po czym i tak rozstrzyga – z dopasowań częściowych, z reguły opartej na jednej cesze albo z całej bazy.

- Codex: „Można ostrożnie przypuszczać, że p+”, mimo że sam stwierdza, iż „bieżące połączenie q−, r− i s+ nie pojawiło się wcześniej” (próba 5).
- Claude indukuje regułę ¬p ∨ ¬q → r i dodaje: „Według niej w h6 r powinno zachodzić, i to podwójnie, bo spełnione są oba warunki” (test 3).
- Gemini: „mam umiarkowane do silnego przekonania, że cecha p nie występuje w bieżącej obserwacji” (T5).
- Qwen3.6: „Prawdopodobieństwo, że p=0, wynosi blisko 100%” (T5#1).

Ciekawe, że na kursowej KB trzy różne systemy sięgnęły po tę samą cechę r: Gemini („Sugeruje to, że r i p wzajemnie się wykluczają”), Qwen3.6 i Qwen3.5 („Nie ma w danych żadnego przykładu sprzecznego z tą regułą (czyli przypadku, gdzie r=1 i p=1)”, T5#2). Wyjątki? Qwen3.5 w T5#1 i T5#3 odpowiedział zgodnie z referencją („nie ma żadnych przesłanek, które pozwoliłyby jednoznacznie stwierdzić, czy w obiekcie W cecha p występuje, czy nie”), a Qwen3.6 raz pozostał neutralny – ale w wariancie dziedzinowym i w siatce oba Qwen w większości rozstrzygały (12/15 i ok. 11/15). Bielik pustej klasy w ogóle nie zauważył (0/15).

**3.7. Uzasadnienie jest zawsze, wiarygodność – nie zawsze.** Poza Bielikiem każdy system uzasadnia odpowiedź i odwołuje się do konkretnych obserwacji. Bywa to mylące: Qwen3.6 zawierał fałszywe twierdzenia poboczne o KB w ok. 34 z 57 odpowiedzi, a Qwen3.5 w ok. 10 z 57 zaczynał od tezy, którą potem sam obalał. Uzasadnienie z liczbami nie gwarantuje więc, że wniosek z niego wynika.

## 4. Różnice między systemami

Oznaczenia: + zgodnie z referencją, ± częściowo, − niezgodnie, n/t – kryterium nie występowało w testach danego systemu.

| System | Klasa warunkowa | Remis | Pusta klasa | Kalibracja siły (bez Know przy małym N) | Druga wartość (Pos słabszej) | Wariant dziedzinowy |
|---|---|---|---|---|---|---|
| Bielik-11B | − | − | − (niezauważona) | − | n/t | odmowa 13/15 |
| Qwen3.6-35B | + | ± (6/9 neutralnie) | − | − (Know przy 5/5) | n/t | wiedza dziedzinowa 6/15 |
| Qwen3.5-122B | + | − / ± | ± (T5: 2/3 neutralnie) | ± | ± (implicite) | wiedza dziedzinowa 5/15, także przy niepustej klasie |
| Claude Opus 5.5 | + | − | − | ± (Bel zamiast Pos, bez Know) | ± | n/t |
| Codex | + | + | − | + | − | n/t |
| gpt-6-luna | ± (8/12) | n/t | n/t | + (17/18 w dopuszczonym zakresie) | − | n/t |
| Gemini | + | + | − | ± (Bel w T3, kategoryczne T2) | ± | n/t |

## 5. Wnioski i rekomendacje dla etapu grupowego

Obraz jest dość spójny. Mocniejsze systemy realizują rdzeń modelu – wybierają klasę warunkową i liczą w niej częstości – a rozchodzą się z referencją dokładnie tam, gdzie model z materiałów sterujących ma reguły mało intuicyjne dla LLM: przy remisie (dwie słabe możliwości zamiast szukania rozstrzygnięcia gdzie indziej), przy pustej klasie (brak przesłanek zamiast uogólnienia z jednej cechy), przy małej próbie (brak Know mimo jednomyślności) i przy komunikatach dwustronnych (Pos słabszej wartości). Te cztery miejsca warto uczynić osią dalszych badań.

Proponujemy:

1. **Wariantowanie KB (MS v02 §2.3.3).** Zmieniać liczebność klas przy stałej proporcji (np. 2:1, 4:2, 20:10 oraz 5:0, 10:0, 20:0). Pozwoli to sprawdzić, czy systemy reagują na N, czy tylko na proporcję, i od jakiej liczebności Know staje się dopuszczalne.
2. **Wariant prompta z prośbą o osobną ocenę p i ¬p** – bezpośredni test asymetrii z p. 3.2.
3. **Dziedzina a symbole.** Rozszerzyć wariant dziedzinowy na kolejne interpretacje (np. drukarka 3D) i sprawdzić, czy wiedza dziedzinowa działa głównie przy pustej klasie, jak u Qwen3.6, czy także przy niepustej, jak u Qwen3.5.
4. **Pytania do prowadzącego.** Potwierdzić odczytanie progów i nierówności 2.12–2.18 oraz to, czy para Pos(p), Pos(¬p) dla pustej klasy jest zamierzoną odpowiedzią referencyjną – od tego zależy ocena wzorca z p. 3.6.
