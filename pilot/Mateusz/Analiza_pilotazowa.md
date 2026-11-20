# Pilotażowa analiza zachowań systemu agAI

System: Claude Opus 5.5 · odpowiedzi zebrane 14.11.2026

## Metoda i punkt odniesienia

Każdy prompt trafił do osobnej, świeżej instancji modelu, bez dostępu do tej analizy. Prompty zawierają tylko symbole p, q, r, s i bazę obserwacji z rys. 0.1. Pytamy o zmienną r, której stan w obserwacji bieżącej jest nieznany (r±). Zbadano kontekst pełny, kontekst pusty i przypadek brzegowy, w którym żadna obserwacja z bazy nie pasuje do kontekstu. Test 1 uruchomiono 3 razy (cytowany jest pierwszy przebieg), testy 2 i 3 po razie.

**Odpowiedź referencyjna (materiały sterujące 2.2–2.3).** Bierzemy obserwacje z bazy zgodne z bieżącą na znanych zmiennych (klasa C) i liczymy siłę przekonania λ(r⁺) = (1 + liczba r⁺ w C) / (2 + |C|), λ(r⁻) = 1 − λ(r⁺).

Progi:

- λ < 0,2 → brak komunikatu,
- [0,2; 0,65) → **Pos**,
- [0,65; 0,9) → **Bel**,
- ≥ 0,9 → **Know**.

Uwagi do materiałów:

- **Progi.** We wzorach 2.15–2.18 materiałów wszystkie progi mają to samo oznaczenie. Wartości przypisano więc w kolejności wymuszonej przez 2.14.
- **Warunek 2.12.** Czytamy go jako λ ≥ λmaxBel.
- **Klasa pusta.** Dla pustej klasy (test 3) wzór stosujemy przez ekstrapolację, bo materiały tego przypadku nie omawiają.

**Markery.**

- **Know:** „jestem pewien”, „na pewno”.
- **Bel:** „sądzę”, „raczej”, „prawdopodobnie”.
- **Pos:** „możliwe”, „nie można wykluczyć”, „przypuszczam z małą pewnością”.

**Skala ocen.**

- **Poprawna:** obie wartości zakomunikowane na poziomie zgodnym z modelem.
- **Częściowo poprawna:** jeden komunikat brakuje albo ma zły poziom, ale uzasadnienie opiera się na klasie C.
- **Niepoprawna:** zły poziom, a uzasadnienie opiera się na danych spoza klasy C.

| Test | Kontekst | Punkt odniesienia | Odpowiedź systemu | Ocena |
|---|---|---|---|---|
| 1 | pełny: p+ q+ s+ | C = {h2, h3}, λ = [0,50; 0,50] → Pos(r), Pos(¬r) | Bel(r) osłabione; ¬r pośrednio | częściowo poprawna |
| 2 | pusty | C = {h1–h5}, λ = [0,71; 0,29] → Bel(r), Pos(¬r) | Bel(r); ¬r tylko jako „nie mam pewności” | częściowo poprawna |
| 3 | pełny: p− q− s+ | C = ∅, λ = [0,50; 0,50] → Pos(r), Pos(¬r) | Bel(r) | niepoprawna |

## Test 1 – kontekst pełny (rys. 0.1)

**Prompt**

```text
Rozważ zmienne zdaniowe p, q, r, s. W każdej obserwacji zmienna może mieć stan + (zachodzi), − (nie zachodzi) albo ± (stan nieznany – nie został zaobserwowany).

Dotychczasowe obserwacje:
h1: p+ q− r+ s+
h2: p+ q+ r− s+
h3: p+ q+ r+ s+
h4: p− q+ r+ s+
h5: p− q+ r+ s+

Bieżąca obserwacja:
h6: p+ q+ r± s+

Polecenie: wyraź w języku naturalnym, co sądzisz o stanie zmiennej r w sytuacji opisanej bieżącą obserwacją h6.
```

**Odpowiedź rzeczywista (przebieg 1 z 3)**

> Nie da się rozstrzygnąć, czy r zachodzi w h6. Mogę najwyżej przypuszczać, że raczej tak, ale z małą pewnością.
>
> **Dlaczego nie da się tego rozstrzygnąć:**
>
> W h6 znane są wartości p+, q+ i s+. Taki sam układ wystąpił wcześniej dwa razy, ale z przeciwnymi wynikami:
>
> - w h2 (p+ q+ s+) r **nie zachodziło**,
> - w h3 (p+ q+ s+) r **zachodziło**.
>
> Obserwacje najbardziej podobne do h6 dzielą się więc pół na pół i nie rozstrzygają sprawy.
>
> **Dlaczego jednak raczej zachodzi:**
>
> - Ogólnie r zachodziło w 4 z 5 obserwacji. Jedynym wyjątkiem jest h2.
> - Gdy zachodziło p, r zachodziło w 2 z 3 przypadków (h1, h3).
> - Gdy zachodziło q, r zachodziło w 3 z 4 przypadków (h3, h4, h5).
> - s zachodziło we wszystkich obserwacjach, więc nic nie mówi o r.
>
> **Wniosek w języku naturalnym:**
>
> „Przypuszczam, że w obecnej sytuacji r prawdopodobnie zachodzi, ale nie jestem tego pewien. Zwykle tak bywało. Jednak przy dokładnie takim samym układzie pozostałych zmiennych zdarzyło się już, że r nie zachodziło. Dlatego traktuję to jako przypuszczenie, a nie pewny wniosek.”

**Najważniejsze spostrzeżenia**

- **Środki językowe:** „raczej tak” i „prawdopodobnie zachodzi” to Bel(r). Bel jest jednak osłabione przez „mogę najwyżej przypuszczać… z małą pewnością”, co jest bliskie Pos(r). Wartość r⁻ nie dostaje jawnego operatora. Jest dopuszczona tylko pośrednio: „nie da się rozstrzygnąć”, „zdarzyło się już, że r nie zachodziło”. Poza klasyfikacją są: „nie jestem pewien” (negacja pewności) i „4 z 5” (liczba).
- **Uzasadnienie:** system poprawnie wskazuje klasę {h2, h3} i remis 1:1, po czym rozstrzyga go danymi spoza klasy (częstości 4/5, 2/3 i 3/4). Pozostałe dwa przebiegi dały ten sam kierunek („raczej”, „najprawdopodobniej”), ale jawnie wyraziły Pos(¬r): „nie można wykluczyć r−”, „dane nie wykluczają, że r nie zachodzi”. Zgodność uzasadnienia z modelem z 2.2.3: częściowa.

**Ocena wstępna: częściowo poprawna.** Model wymaga dwóch słabych możliwości, Pos(r) i Pos(¬r). System komunikuje przewagę r⁺, której klasa C nie uzasadnia.

## Test 2 – kontekst pusty

**Prompt:** jak w teście 1, ale z obserwacją bieżącą `h6: p± q± r± s±`.

**Odpowiedź rzeczywista**

> W bieżącej sytuacji h6 nie zaobserwowano żadnej zmiennej, więc nie wiem na pewno, czy r zachodzi. Mogę tylko oprzeć się na wcześniejszych obserwacjach.
>
> **Wniosek:** sądzę, że r **raczej zachodzi**, ale nie mam co do tego pewności.
>
> **Dlaczego tak sądzę:**
>
> - W dotychczasowych pięciu obserwacjach r zachodziło cztery razy (h1, h3, h4, h5) i nie zachodziło tylko raz (h2). Częstość r+ wynosi więc 4/5, czyli około 80%.
> - Jedyny przypadek bez r (h2) wystąpił, gdy jednocześnie zachodziły p i q. Jednak w h3 przy p+ i q+ r zachodziło, więc nie da się z tego wyprowadzić reguły. Poza tym w h6 stany p i q też są nieznane, więc i tak nie da się tego tutaj zastosować.
> - Zmienna s zachodziła we wszystkich obserwacjach, niezależnie od r, więc nic nie mówi o r.
>
> **Zastrzeżenie:** to wniosek oparty na pięciu obserwacjach. Jest odwoływalny i trzeba go zrewidować, gdy tylko pojawi się jakakolwiek informacja o h6, zwłaszcza bezpośrednia obserwacja r.

**Najważniejsze spostrzeżenia**

- **Środki językowe:** „sądzę, że r raczej zachodzi” to Bel(r). Poza klasyfikacją są: „nie wiem na pewno”, „nie mam pewności” (negacja pewności), „około 80%” (liczba) i „wniosek odwoływalny”.
- **Uzasadnienie:** system zauważa, że kontekst jest pusty, i opiera się na całej bazie. Słusznie odrzuca regułę wyprowadzoną z jednej obserwacji (h2). Zgodność z modelem z 2.2.2: tak, bo klasa C to cała baza. System liczy surową częstość 4/5, a model daje 5/7. Oba wyniki mieszczą się jednak w przedziale Bel.

**Ocena wstępna: częściowo poprawna (niepełna).** Bel(r) zgadza się z modelem. Brakuje jawnego Pos(¬r), bo system podaje tylko negację pewności („nie mam pewności”).

## Test 3 – brak pasujących obserwacji

**Prompt:** jak w teście 1, ale z obserwacją bieżącą `h6: p− q− r± s+`. Układ p− q− s+ nie występuje w bazie.

**Odpowiedź rzeczywista**

> **Przypuszczam, że w sytuacji h6 r zachodzi, ale nie mam co do tego pewności.**
>
> **Dlaczego tak sądzę:**
>
> - We wszystkich obserwacjach, w których p nie zachodzi (h4, h5), r zachodziło.
> - W jedynej obserwacji, w której q nie zachodzi (h1), r także zachodziło.
> - r nie zachodziło tylko raz (h2), gdy p i q zachodziły jednocześnie. W h6 nie zachodzi ani p, ani q, czyli jest to sytuacja najbardziej odległa od h2.
> - s zachodzi we wszystkich obserwacjach, więc nic nie mówi o r.
>
> Dotychczasowe obserwacje pasują więc do prawidłowości: „jeśli nie zachodzi p albo nie zachodzi q, to zachodzi r”. Według niej w h6 r powinno zachodzić, i to podwójnie, bo spełnione są oba warunki.
>
> **Dlaczego nie mam pewności:**
>
> - Obserwacji jest tylko pięć.
> - Połączenie „p nie zachodzi i q nie zachodzi” nie pojawiło się w nich ani razu. Wnioskuję więc o przypadku, którego jeszcze nie widziałem.
> - Nawet w h3, gdy p i q zachodziły, r też zachodziło. Nie wiadomo więc dokładnie, od czego zależy r, a obserwacje nie wykluczają innych wyjaśnień.
>
> Uważam zatem, że r w h6 raczej zachodzi, ale jest to wniosek z dotychczasowych obserwacji, a nie pewność. Rozstrzygnęłaby to dopiero obserwacja r albo kolejne przypadki, w których p i q nie zachodzą.

**Najważniejsze spostrzeżenia**

- **Środki językowe:** „raczej zachodzi” to Bel(r). „Przypuszczam” jest niejednoznaczne (Bel albo Pos). Poza klasyfikacją są: „r powinno zachodzić” (modalność predykcyjna) i „nie mam pewności” (negacja pewności).
- **Uzasadnienie:** system zauważa, że układu p− q− nie było w bazie, i zaznacza niepewność. Mimo to indukuje regułę ¬p ∨ ¬q → r. Reguła jest zgodna z h1, h4 i h5, ale opiera się na obserwacjach spoza klasy, a model referencyjny takiego uogólnienia nie przewiduje. „I to podwójnie” to nadinterpretacja: spełnienie obu członów alternatywy nie wzmacnia wniosku z reguły. Zgodność z modelem z 2.2.3: nie.

**Ocena wstępna: niepoprawna.** Model daje Pos(r) i Pos(¬r), czyli obie możliwości są równie słabe. System komunikuje Bel(r), opierając się na danych spoza klasy C.

## Wnioski

- **Mocne strony:** w każdym z 5 przebiegów system uzasadnił odpowiedź i zaczął od porównania z kontekstem h6. W żadnym nie użył Know i nie zakomunikował jednocześnie Bel(r) i Bel(¬r), co jest zgodne z regułą pragmatyczną z 2.3.2.
- **Słabość:** system sygnalizuje niepewność, ale na niej nie poprzestaje. Przy remisie (test 1) i przy pustej klasie (test 3) sięga po dane spoza klasy warunkowej i komunikuje Bel tam, gdzie model wymaga dwóch Pos.
- **Asymetria:** wartość przeciwną (r⁻) system wyraża zwykle pośrednio, negacją pewności („nie jestem pewien”), a rzadziej jawnym „nie można wykluczyć”.
- **Ograniczenia:**
  - Testy 2 i 3 uruchomiono po razie.
  - Klasyfikacji dokonał badany model, a zweryfikował ją niezależny recenzent: model Claude Fable 5.2.
  - Polecenie „co sądzisz” mogło sprzyjać użyciu markera Bel („sądzę”).
