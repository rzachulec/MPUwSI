# Podsumowanie indywidualne – Bielik-11B-v3.1 vs Qwen3.6-35B-A3B vs Qwen3.5-122B-A10B

> Dokument przygotowany z pomocą LLM (Claude Opus 5.5) na podstawie `report/*.md`. Klasyfikacje i oceny zweryfikowane przez autora.

**Zakres (dla każdego z 3 modeli):** T1–T5 powtórzone trzy razy, D1–D5 również (interpretacja dziedzinowa CI/build), do tego siatka wszystkich 27 możliwych kontekstów. Razem 57 odpowiedzi na model, każda w nowej sesji, temperature 0.7, ten sam dostawca (ark-labs.cloud), ten sam dzień (2026-11-20).

## Porównanie w liczbach

| miara | Bielik-11B-v3.1 | Qwen3.6-35B-A3B | Qwen3.5-122B-A10B |
|---|---|---|---|
| T1–T5: zgodne z referencją (konkluzja) | 4/15 (wszystkie z błędnym uzasadnieniem) + 1 częściowo | 7/15 | 7/15 (w tym 1 z niespójnym nagłówkiem) |
| T1–T5: sprzeczne kierunkowo | 5/15 | 0/15 | 0/15 (wniosek końcowy) |
| T1–T5: zbyt pewne | 3/15 | **6/15** + 1 lekko | 4/15 |
| T1–T5: zbyt ostrożne / odmowa | 2/15 | 0/15 | 2/15 |
| T1–T5: niespójne | – | 1/15 | 2/15 |
| T2 (B3 = 0/5 → Bel(¬p)) trafione | 0/3 | 1/3 (2× Know: „bliskie pewności”, „100%”) | **3/3** |
| Klasa warunkowa poprawnie wyznaczona (T2–T5) | 0/12 | 11/12 (2× pominięty u8) | 11/12 (T3#3 po autokorekcie) |
| Siatka: konteksty z ref. Bel(¬p) trafione | 2/7 | 3/7 (4 zbyt pewne – Know) | 4/7 (3 zbyt ostrożne) |
| Pusta klasa zauważona (T5, D5, 9 z siatki) | 0/15 | 14/15 (nie: T5#2) | ok. 12/15 |
| Pusta klasa → mimo to silne przekonanie | 4/15 | 12/15 (neutralnie 1, słaba przewaga 2) | ok. 11/15 |
| Wariant D: odmowa jako wniosek końcowy | 13/15 | 0/15 | 3/15 (tylko D1) |
| Wyraźne ślady wiedzy dziedzinowej | brak | 6/15 (D2#2, D2#3, D4#3, D5 ×3); rozstrzygająca w 2 (D5#2, D5#3) | 5/15 (D3#1, D3#3, D4#2, D4#3, D5#2) |
| Halucynacje dot. zawartości KB (T+D) | ok. 10/30 | ok. 18/30 przy liczeniu także fałszów pobocznych; w rachunku klasy 4/30 (T2#2, T2#3, T5#2, D2#2)* | ok. 10/30 (inne w charakterze, patrz niżej) |
| Odpowiedzi zdegenerowane | 1 (D4#1, urwana) | 0 | 1 (D4#2, pętla do 16 384 tokenów) |
| Niespójność nagłówek–wniosek | rzadko | 3/57 (T1#2, C q±r−s−, C q+r−s±) | ok. 10/57 |
| Mediana długości odpowiedzi\* | 365 tokenów | 1358 tokenów | 729 tokenów |

\* Dla Qwen3.6 liczone po pełnej ponownej lekturze, łącznie z fałszywymi twierdzeniami w analizie pobocznej. Dla Bielika i Qwen3.5 liczone głównie halucynacje wpływające na rachunek, więc ten wiersz nie jest porównywalny 1:1.

## Bielik-11B-v3.1: wzorce

1. **Kontekst q, r, s ignorowany.** W żadnej z 12 odpowiedzi T2–T5 model nie wyznaczył klasy warunkowej. Jeśli coś liczy, to po całej KB (4 / 8), np. w T3#3 wnioskuje ¬p z globalnej proporcji, choć w B4 przeważa p (2/1). Deklaracje użycia kontekstu (T2#3, T4#2, T5#3) są fałszywe.
2. **Błędy arytmetyczne i halucynacje danych.** „4 z 12 to większość” (T1#2, T1#3), zmyślone wartości p w wierszach (T2#2, T2#3, T4#2), zmyślone liczności w wariancie D (8/12, 7/5, 6/12, 6/6 zamiast 4/8).
3. **„?” traktowane jako przeszkoda.** Typowe *„stan p jest nieznany, więc nie można stwierdzić”*. W T5#3 „nie zaobserwowano” utożsamione z „nie występuje”.
4. **Puste klasy nigdy niesygnalizowane.** W 0/15 przypadków model zauważył, że kombinacja nie wystąpiła w KB.
5. **Niestabilność i niespójności.** Przeciwne kierunki w powtórzeniach; „Tak, … nie występuje”.
6. **Wariant D:** prawie same odmowy (13/15), bez wpływu wiedzy dziedzinowej.

## Qwen3.6-35B-A3B: wzorce

1. **Rdzeń modelu realizowany.** W 11/12 odpowiedzi T2–T5 jawnie wyznacza klasę warunkową (wiersz po wierszu). Struktura *analiza → wniosek*, więc niespójności nagłówek–wniosek tylko 3/57. Najdłuższe odpowiedzi (mediana ok. 1360 tokenów).
2. **Najlepszy przy 2:1 i remisach.** T3, D3 i 6 kontekstów siatki z przewagą 2:1 → p z umiarkowaną siłą („najprawdopodobniej”). Remisy w 6/9 kończą się neutralnością; w 3/9 rozstrzygnięte priorem 8/12 lub Naive Bayes (T4#1, D4#1, D4#2).
3. **Przeszacowanie przy klasie jednomyślnej.** 5/5 daje „bliskie pewności”, „100%”, „ryzyko zerowe” (T2#2, T2#3, D2#3, 4 konteksty siatki), czyli Know, nieosiągalne przy N = 12.
4. **Pusta klasa zauważona (14/15), ale ignorowana.** Tylko raz neutralnie; zwykle rozstrzyga regułą „r=1 ⇒ p=0”, regułą zmyśloną albo uznaje nową kombinację za „błąd pomiarowy”.
5. **Wiedza dziedzinowa w 6/15 odpowiedzi D, bez odmów.** Przy niepustej klasie tylko wzmacnia pewność zgodną z danymi (D2); rozstrzyga wyłącznie przy pustej klasie (D5: p=0, p=1, p=1).
6. **Liczne fałsze poboczne o KB** (ok. 34/57, np. „gdy q=1, p zawsze 1”). Zwykle nie zmieniają wniosku, ale podważają wiarygodność uzasadnienia; w kilku kontekstach siatki go wyznaczają.

## Qwen3.5-122B-A10B: wzorce

1. **Rdzeń modelu realizowany.** W 11/12 odpowiedzi T2–T5 wyznacza klasę warunkową i liczy p+/p−. T2 3/3 Bel(¬p); T2#3 wprost zauważa, że 5/5 przy N = 12 to nie pewność.
2. **Teza przed analizą → niespójność.** Ok. 10/57 odpowiedzi zaczyna od wniosku, który analiza potem obala („Moja wcześniejsza analiza … była błędna”); odbiorca dostaje jednocześnie Bel(p) i Bel(¬p).
3. **Remis i pusta klasa rozstrzygane spoza klasy.** Przy 2:2 sięga do klasy częściowej lub całej KB (T4#1, T4#3). Pustą klasę zauważa, ale zastępuje regułą jednej cechy; neutralnie tylko T5#1, T5#3, a D5 daje ¬p, p, ¬p.
4. **Halucynacje klas i zawyżone słownictwo.** Zmyślona klasa (C q−r−s−), zgubione u5 (D3#2, D3#3 → „100%”, Know); „ryzyko błędu 0%” przy 5/5.
5. **Wiedza dziedzinowa wpływa na wniosek także przy niepustej klasie** (5/15): „piątkowe commity … obarczone ryzykiem” (D4#2) daje przy remisie 2/2 „z bardzo wysokim prawdopodobieństwem niepowodzenie”. D4#2 wpadł w pętlę do limitu tokenów.

## Wniosek

- **Bielik-11B** nie realizuje modelu z materiałów sterujących: nie tworzy klasy warunkowej, nie liczy w niej częstości, a jego środki modalne nie są skalibrowane. Trafienia wynikają z ogólnej asekuracji. Jest użyteczny jako dolny punkt odniesienia.
- **Qwen3.5-122B** realizuje rdzeń modelu (klasa warunkowa + częstość) i w przypadkach z wyraźnym sygnałem (B3) odpowiada zgodnie z referencją. Błędy dotyczą miejsc, gdzie model z materiałów ma reguły „nieintuicyjne” dla LLM: remis w klasie (→ dwie słabe możliwości, a nie szukanie rozstrzygnięcia gdzie indziej), pusta klasa (→ brak przesłanek, a nie uogólnianie z jednej cechy) i mała próba (→ brak Know). Dochodzą do tego niespójności wynikające z pisania tezy przed analizą.
- **Qwen3.6-35B** także realizuje rdzeń modelu, a przy przewagach 2:1 i remisach jest najlepszy z trzech. Jego główną wadą jest przeszacowanie: jednomyślna klasa i pusta klasa prowadzą do „bliskie pewności” / „100%”, czyli do Know, którego referencja przy N = 12 nigdy nie daje. Model 122B przy tych samych danych częściej pisze Bel, ale bywa niespójny.
- **Ranking zależy od kryterium.** Dla zgodności kierunku i klasy oba Qwen ≫ Bielik. Dla kalibracji modalności przy silnym sygnale 122B > 35B. Dla spójności i trafności przy słabym sygnale 35B > 122B. Żaden model nie radzi sobie z pustą klasą zgodnie z referencją.
- **Wariant dziedzinowy** różnicuje modele: najsłabszy reaguje odmową, oba Qwen wiedzą dziedzinową, z podobną częstością (5/15 i 6/15). U modelu 122B wpływa ona na odpowiedź także przy niepustej klasie (D4: przy remisie 2/2 nagłówki „z bardzo wysokim prawdopodobieństwem niepowodzenie”). Model 35B przy niepustej klasie używa jej tylko jako wzmocnienia zgodnego z danymi (D2), a rozstrzyga nią wyłącznie przy pustej klasie (D5).

Proponowane następne kroki:
- powtórzenie z `temperature=0`, żeby oddzielić niestabilność od błędów systematycznych;
- wariant prompta z prośbą o podanie wniosku *na końcu*, co powinno ograniczyć niespójność nagłówek–wniosek u Qwena;
- porównanie z lokalnym modelem średniej wielkości (np. Qwen ~27B);
- wariant prompta z prośbą o oddzielne oszacowanie szansy p i ¬p, żeby sprawdzić, czy modele „widzą” obie składowe holonu.
