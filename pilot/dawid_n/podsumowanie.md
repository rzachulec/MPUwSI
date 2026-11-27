# Pilotażowa analiza zachowań systemu agAI

## Warunki badania

- Badany system — Google Gemini. Model według zapisu testującego — **Gemini 4 Hydrogen**.
- Interfejs — darmowy czat w przeglądarce. Język promptów — polski.
- Wszystkie testy przeprowadzono 27.11.2026 między 13:30 a 14:00 czasu polskiego.
- Każdy z pięciu promptów wysłano jako jedyną wiadomość testową w osobnym czacie tymczasowym Gemini.

### Proponowana interpretacja dziedzinowa

Obiekt W to drukarka 3D, a pojedyncza obserwacja opisuje jedno uruchomienie wydruku.

| Cecha | Znaczenie |
| --- | --- |
| p | Pierwsza warstwa poprawnie przylega do stołu. |
| q | Użyto filamentu PETG. |
| r | Drukowano w zamkniętej komorze. |
| s | Przed wydrukiem wypoziomowano stół. |

Interpretacja jest robocza i wymaga uzgodnienia z grupą. Prompty operują wyłącznie na symbolach p, q, r, s.

## Punkt odniesienia

Dla T1 bierzemy całą bazę. W T2–T5 wybieramy klasę obserwacji o dokładnie tych samych wartościach q, r, s co w obserwacji bieżącej. W tej klasie liczymy wartości p = 1 (n+) i p = 0 (n−). Holon ma składowe λ(p+) = (1 + n+) / (2 + n+ + n−) oraz λ(p−) = (1 + n−) / (2 + n+ + n−).

Do każdej składowej osobno stosujemy progi z [instrukcji repozytorium](../pilot_README.md).

| Zakres λ | Modalność |
| --- | --- |
| poniżej 0,20 | brak komunikatu |
| od 0,20 do poniżej 0,65 | Pos, słaba możliwość |
| od 0,65 do poniżej 0,90 | Bel, silna możliwość |
| od 0,90 | Know, pewność |

W T5 stosujemy wzór także do pustej klasy. Daje to tę samą parę wartości co remis w T4, lecz w T5 żadna obserwacja nie pasuje do kontekstu.

W analizie przypisano modalność frazom o **bieżącym** stanie p lub ¬p i wskazano sformułowania bez jednoznacznej klasyfikacji. Oceniono wybór klasy, zliczenia oraz siłę komunikatów względem punktu odniesienia.

## Testy

### T1 — Kontekst pusty

**Prompt**

```text
Rozważ obiekt W opisany czterema cechami p, q, r i s. W obserwacji 1 oznacza, że cecha występuje, 0 oznacza, że cecha nie występuje, a ? oznacza, że jej stanu nie zaobserwowano.

Poniżej podano kompletne obserwacje historyczne obiektu W.

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

W bieżącej obserwacji zapisano p = ?, q = ?, r = ?, s = ?.

Na podstawie tych danych wyraź w języku naturalnym swoje przekonanie o tym, czy cecha p występuje w obiekcie W w bieżącej obserwacji.
```

**Odpowiedź rzeczywista**

```text
Na podstawie dostępnych danych historycznych uważam, że wystąpienie cechy p w bieżącej obserwacji jest mało prawdopodobne (szacowane na około 33%).

Uzasadnienie

Ponieważ w bieżącej obserwacji stan wszystkich pozostałych cech (q, r, s) jest nieznany (?), jedyną podstawą do oceny jest ogólna częstość występowania cechy p w przeszłości:
• Liczba wszystkich obserwacji: 12 (od u1 do u12)
• Wystąpienie cechy p (1): w 4 przypadkach (u1–u4), co stanowi 33,3% obserwacji
• Brak cechy p (0): w 8 przypadkach (u5–u12), co stanowi 66,7% obserwacji
Brak wiedzy o wartościach pozostałych cech uniemożliwia wykorzystanie silnych zależności widocznych w tabeli (np. tego, że wystąpienie cechy r zawsze wykluczało p). W tej sytuacji bardziej uzasadnione jest założenie, że cecha p nie występuje, choć jej obecności nie można całkowicie wykluczyć.
Jeśli wiesz, jaki jest stan którejkolwiek z pozostałych cech (q, r lub s), podaj ją – pozwoli to znacznie precyzyjniej określić szanse na wystąpienie cechy p.
```

**Odpowiedź referencyjna**

Klasa B0∅ (u1–u12), n+ = 4, n− = 8, holon [5/14, 9/14] → **Pos(p), Pos(¬p)**. λ(p−) = 9/14 jest tuż poniżej progu 0,65.

**Najważniejsze spostrzeżenia**

- „jej obecności nie można całkowicie wykluczyć” komunikuje Pos(p). „bardziej uzasadnione jest założenie, że cecha p nie występuje” wskazuje na ¬p, ale określa względną przewagę i pozostawia jej siłę niejednoznaczną.
- „szacowane na około 33%” to oszacowanie liczbowe. Wzmianka o zależności od r dotyczy obserwacji historycznych.
- Gemini rozpoznaje pusty kontekst i poprawnie zlicza 4 wystąpienia oraz 8 braków p w całej bazie. Podaje częstości 4/12 i 8/12. Wygładzenie referencyjne daje 5/14 i 9/14.
- **Ocena wstępna — częściowo zgodna.** Pos(p) jest wyrażone wprost. Dla ¬p model wskazuje przewagę bez jednoznacznego komunikatu Pos(¬p), którego wymaga λ(p−) = 9/14.

### T2 — Kontekst pełny z przewagą ¬p

**Prompt**

```text
Rozważ obiekt W opisany czterema cechami p, q, r i s. W obserwacji 1 oznacza, że cecha występuje, 0 oznacza, że cecha nie występuje, a ? oznacza, że jej stanu nie zaobserwowano.

Poniżej podano kompletne obserwacje historyczne obiektu W.

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

W bieżącej obserwacji zapisano p = ?, q = 0, r = 1, s = 1.

Na podstawie tych danych wyraź w języku naturalnym swoje przekonanie o tym, czy cecha p występuje w obiekcie W w bieżącej obserwacji.
```

**Odpowiedź rzeczywista**

```text
Jest bardzo mało prawdopodobne (prawie niemożliwe), aby cecha p występowała w obiekcie W w bieżącej obserwacji.
Wynika to z następujących przesłanek płynących z danych historycznych:
• Identyczne przypadki z przeszłości: W historii zarejestrowano aż 5 obserwacji o dokładnie takim samym układzie znanych cech (\(q = 0, r = 1, s = 1\)), czyli przypadki u6, u7, u8, u11 oraz u12. W każdym z tych przypadków cecha p nie występowała (\(p = 0\)).
• Rola cechy r: W całym zbiorze danych nigdy nie zdarzyło się, aby cechy p oraz r występowały jednocześnie. Ilekroć cecha r była obecna (\(r = 1\)), cecha p była nieobecna (\(p = 0\)).
Wszystkie dostępne dane jednoznacznie wskazują, że w bieżącej obserwacji cecha p nie występuje (\(p = 0\)).
Jeśli chcesz, mogę również:
• Obliczyć dokładne prawdopodobieństwa warunkowe (np. za pomocą naiwnego klasyfikatora Bayesa)
• Wyznaczyć reguły decyzyjne (np. drzewo decyzyjne) dla tego zbioru danych
```

**Odpowiedź referencyjna**

Klasa B3 (u6, u7, u8, u11, u12), n+ = 0, n− = 5, holon [1/7, 6/7] → **Bel(¬p)**. λ(p+) = 1/7 jest poniżej progu 0,20.

**Najważniejsze spostrzeżenia**

- „bardzo mało prawdopodobne (prawie niemożliwe)” dotyczy p i pośrednio wyraża silne przekonanie o ¬p. Końcowe „jednoznacznie wskazują, że w bieżącej obserwacji cecha p nie występuje” brzmi jak Know(¬p).
- „prawie niemożliwe” opisuje bardzo niską wiarygodność p. Ta fraza nie daje jednoznacznego przypisania p do Know, Bel lub Pos.
- Gemini poprawnie wybiera wszystkie pięć obserwacji z B3 i zlicza 0 wystąpień oraz 5 braków p. Dodatkowy argument o r = 1 odnosi się tutaj do tych samych pięciu obserwacji.
- **Ocena wstępna — właściwy kierunek, zbyt kategoryczna końcówka.** Holon daje Bel(¬p), ponieważ 6/7 jest poniżej progu Know, a 1/7 jest poniżej progu Pos dla p. Początek sygnalizuje bardzo małą szansę p, a końcówka brzmi jak rozstrzygnięcie.

### T3 — Kontekst pełny z przewagą p

**Prompt**

```text
Rozważ obiekt W opisany czterema cechami p, q, r i s. W obserwacji 1 oznacza, że cecha występuje, 0 oznacza, że cecha nie występuje, a ? oznacza, że jej stanu nie zaobserwowano.

Poniżej podano kompletne obserwacje historyczne obiektu W.

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

W bieżącej obserwacji zapisano p = ?, q = 1, r = 0, s = 0.

Na podstawie tych danych wyraź w języku naturalnym swoje przekonanie o tym, czy cecha p występuje w obiekcie W w bieżącej obserwacji.
```

**Odpowiedź rzeczywista**

```text
Cecha p prawdopodobnie występuje w obiekcie W, ponieważ w identycznych sytuacjach w przeszłości pojawiała się ona dwukrotnie częściej niż jej brak.

Analiza danych historycznych

W bieżącej obserwacji znane cechy to: q = 1, r = 0, s = 0. W historii obserwacji dokładnie taki układ wystąpił trzy razy:
• u3: p = 1 (cecha występuje)
• u4: p = 1 (cecha występuje)
• u5: p = 0 (cecha nie występuje)

Wnioski

• Wystąpienie cechy (p = 1): 2 z 3 przypadków (ok. 66,7% szans).
• Brak cechy (p = 0): 1 z 3 przypadków (ok. 33,3% szans).
Choć nie można mieć całkowitej pewności, dotychczasowe dane wyraźnie wskazują, że p = 1 jest bardziej prawdopodobnym stanem.
Czy chcesz, abym:
• Przeanalizował zależności między wszystkimi cechami w tabeli
• Zastosował konkretny algorytm klasyfikacji (np. naiwny klasyfikator Bayesa lub drzewo decyzyjne)
Daj znać, jeśli potrzebujesz bardziej formalnego ujęcia matematycznego.
```

**Odpowiedź referencyjna**

Klasa B4 (u3, u4, u5), n+ = 2, n− = 1, holon [3/5, 2/5] → **Pos(p), Pos(¬p)**. Obie składowe mieszczą się w przedziale Pos.

**Najważniejsze spostrzeżenia**

- „Cecha p prawdopodobnie występuje” komunikuje Bel(p). Brak p pojawia się w zestawieniu liczbowym, bez jawnej frazy wyrażającej Pos(¬p).
- „ok. 66,7% szans” i „ok. 33,3% szans” to oszacowania liczbowe. „nie można mieć całkowitej pewności” wyklucza pewność i pozostawia siłę przekonania nieokreśloną.
- Gemini poprawnie wybiera B4 i liczy 2 wystąpienia oraz 1 brak p. Przenosi surowe częstości 2/3 i 1/3 na ocenę bieżącego stanu. Po wygładzeniu λ(p+) wynosi 3/5 i pozostaje poniżej progu Bel.
- **Ocena wstępna — zbyt silne przekonanie o p.** Punkt odniesienia przewiduje słabą możliwość dla obu stanów. Gemini wyraża Bel(p), a ¬p przedstawia liczbowo.

### T4 — Kontekst pełny z remisem

**Prompt**

```text
Rozważ obiekt W opisany czterema cechami p, q, r i s. W obserwacji 1 oznacza, że cecha występuje, 0 oznacza, że cecha nie występuje, a ? oznacza, że jej stanu nie zaobserwowano.

Poniżej podano kompletne obserwacje historyczne obiektu W.

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

W bieżącej obserwacji zapisano p = ?, q = 0, r = 0, s = 1.

Na podstawie tych danych wyraź w języku naturalnym swoje przekonanie o tym, czy cecha p występuje w obiekcie W w bieżącej obserwacji.
```

**Odpowiedź rzeczywista**

```text
Nie mam pewności, czy cecha p występuje – szanse wynoszą dokładnie 50 na 50 (tyle samo przemawia za jej wystąpieniem, co za jej brakiem).

Uzasadnienie na podstawie danych

W bieżącej obserwacji znany układ pozostałych cech to q = 0, r = 0, s = 1. W historii obiektu W dokładnie taka kombinacja wystąpiła czterokrotnie:
• u1: p = 1 (cecha wystąpiła)
• u2: p = 1 (cecha wystąpiła)
• u9: p = 0 (cecha nie wystąpiła)
• u10: p = 0 (cecha nie wystąpiła)
Ponieważ w identycznych warunkach cecha p pojawiała się w połowie przypadków (2 z 4), dane historyczne nie pozwalają jednoznacznie rozstrzygnąć jej obecności i wskazują na pełną niepewność.
Jeśli potrzebujesz wyrażenia tego przekonania w konkretnym formalizmie (np. jako przedział ufności, funkcję masy w teorii Dempstera-Shafera lub zbiór przybliżony), daj znać, a dostosuję odpowiedź do wymaganego modelu.
kod
python
data = [
    ("u1", 1, 0, 0, 1),
    ("u2", 1, 0, 0, 1),
    ("u3", 1, 1, 0, 0),
    ("u4", 1, 1, 0, 0),
    ("u5", 0, 1, 0, 0),
    ("u6", 0, 0, 1, 1),
    ("u7", 0, 0, 1, 1),
    ("u8", 0, 0, 1, 1),
    ("u9", 0, 0, 0, 1),
    ("u10", 0, 0, 0, 1),
    ("u11", 0, 0, 1, 1),
    ("u12", 0, 0, 1, 1),
]

matching = [row for row in data if row[2] == 0 and row[3] == 0 and row[4] == 1]
p_1 = sum(1 for row in matching if row[1] == 1)
p_0 = sum(1 for row in matching if row[1] == 0)
total = len(matching)

print("Matching rows:", matching)
print(f"p=1: {p_1}/{total} ({p_1/total:.2%})")
print(f"p=0: {p_0}/{total} ({p_0/total:.2%})")
```

**Odpowiedź referencyjna**

Klasa B1 (u1, u2, u9, u10), n+ = 2, n− = 2, holon [1/2, 1/2] → **Pos(p), Pos(¬p)**. Pasujące obserwacje dają remis 2 do 2.

**Najważniejsze spostrzeżenia**

- „tyle samo przemawia za jej wystąpieniem, co za jej brakiem” dopuszcza oba stany i pragmatycznie odpowiada parze Pos(p) i Pos(¬p).
- „dokładnie 50 na 50” jest oszacowaniem liczbowym. „Nie mam pewności” oraz „pełną niepewność” sygnalizują brak rozstrzygnięcia bez przypisania osobnej modalności do p i ¬p.
- Gemini poprawnie wybiera B1, zlicza remis 2 do 2 i na nim opiera uzasadnienie. W tym przypadku częstości i składowe holonu są równe po 1/2.
- **Ocena wstępna — zasadniczo zgodna.** Odpowiedź zachowuje symetrię obu stanów i komunikuje brak podstaw do rozstrzygnięcia. Sformułowanie „dokładnie 50 na 50” przenosi jednak dokładną proporcję z czterech obserwacji na szansę stanu bieżącego.

### T5 — Kontekst pełny z pustą klasą

**Prompt**

```text
Rozważ obiekt W opisany czterema cechami p, q, r i s. W obserwacji 1 oznacza, że cecha występuje, 0 oznacza, że cecha nie występuje, a ? oznacza, że jej stanu nie zaobserwowano.

Poniżej podano kompletne obserwacje historyczne obiektu W.

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

W bieżącej obserwacji zapisano p = ?, q = 1, r = 1, s = 1.

Na podstawie tych danych wyraź w języku naturalnym swoje przekonanie o tym, czy cecha p występuje w obiekcie W w bieżącej obserwacji.
```

**Odpowiedź rzeczywista**

```text
Na podstawie danych historycznych mam umiarkowane do silnego przekonania, że cecha p nie występuje w bieżącej obserwacji (\(p = 0\)), choć dane nie pozwalają stwierdzić tego z całkowitą pewnością.

Analiza danych historycznych

• Brak identycznego przypadku: Kombinacja \(q = 1, r = 1, s = 1\) nie pojawiła się dotąd w historii obserwacji, więc nie można podać jednoznacznej reguły z 100% pewnością.
• Kluczowy wpływ cechy r: We wszystkich pięciu przypadkach, w których cecha r występowała (\(r = 1\), obserwacje u6–u8 oraz u11–u12), cecha p była nieobecna (\(p = 0\)). Sugeruje to, że r i p wzajemnie się wykluczają.
• Niejednoznaczna rola cechy q: Obecność cechy q (\(q = 1\)) wiązała się z występowaniem p dwukrotnie (u3, u4), ale raz cecha p nie wystąpiła (u5). Ponadto w tych przypadkach \(r\) oraz \(s\) miały wartość \(0\), co różni się od bieżącej sytuacji.
• Tendencja ogólna oraz cecha s: W całym zbiorze danych brak cechy p jest dwukrotnie częstszy niż jej obecność (8 razy \(p = 0\) wobec 4 razy \(p = 1\)). Gdy cecha s występowała (\(s = 1\)), cecha p była nieobecna w 7 na 9 przypadków.

Podsumowanie

W bieżącej obserwacji występują jednocześnie cechy r oraz s, które w przeszłości silnie wiązały się z brakiem cechy p. Jedynie obecność cechy q wprowadza niewielką niepewność, ponieważ w innych warunkach sprzyjała ona występowaniu p. Z tego względu najbardziej uzasadnione jest stwierdzenie, że cecha p najprawdopodobniej nie występuje.
Jeśli chcesz, możemy rozwinąć tę analizę:
• Obliczyć dokładne prawdopodobieństwo za pomocą naiwnego klasyfikatora Bayesa
• Wyznaczyć formalne reguły decyzyjne (np. metodą zbiorów przybliżonych)
• Zbudować proste drzewo decyzyjne dla tych danych
Daj znać, które podejście Cię interesuje.
```

**Odpowiedź referencyjna**

Klasa B7 (∅), n+ = 0, n− = 0, holon [1/2, 1/2] → **Pos(p), Pos(¬p)**. Obie składowe wynikają z przyjętego wzoru przy zerowych licznikach.

**Najważniejsze spostrzeżenia**

- „mam umiarkowane do silnego przekonania, że cecha p nie występuje” komunikuje Bel(¬p). Gemini nie formułuje osobno Pos(p).
- „dane nie pozwalają stwierdzić tego z całkowitą pewnością” sygnalizuje ograniczenie wniosku bez przypisania p do jednej z modalności. Liczby 8 do 4 i 7 na 9 opisują dane historyczne.
- Gemini rozpoznaje pustą klasę B7, po czym opiera wniosek na obserwacjach zgodnych tylko na części cech i na częstości z całej bazy. Przytaczane zliczenia są poprawne. Uogólnienie wykracza poza klasę warunkową przyjętą w punkcie odniesienia.
- **Ocena wstępna — niezgodna z punktem odniesienia.** Bel(¬p) sugeruje przewagę, której pusta klasa nie dostarcza. Przyjęty wzór zwraca po 1/2, czyli dwie słabe możliwości.

## Podsumowanie indywidualne

Gemini uzasadnił odpowiedź w każdym z pięciu testów. W T1 właściwie użył całej bazy. W T2–T4 poprawnie wybrał obserwacje zgodne ze wszystkimi znanymi cechami i zliczył wartości p. W T2 końcowe sformułowanie było bardziej kategoryczne niż referencyjne Bel(¬p). W T3 surowa częstość 2/3 towarzyszyła Bel(p), podczas gdy składowa holonu 3/5 odpowiadała Pos(p).

W T4 i T5 holon wyniósł [1/2, 1/2], ale z różnych powodów. Przy remisie Gemini przedstawił oba stany jako równorzędne. Po rozpoznaniu pustej klasy sięgnął po częściowo podobne obserwacje i wyraził Bel(¬p). To najsilniejsza rozbieżność między sposobem uzasadnienia Gemini a regułą wyboru klasy warunkowej w modelu referencyjnym.

Zapis obejmuje po jednym przebiegu dla każdego kontekstu. Na tej podstawie można porównać pięć zebranych odpowiedzi. Stabilność sformułowań przy powtórzeniach pozostaje nieoceniona.
