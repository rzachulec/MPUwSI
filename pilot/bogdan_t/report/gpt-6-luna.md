# Analiza pilotażowa modelu gpt-6-luna

Bohdan Tkachenko, nr indeksu 256630

## Dane i przebieg prób

Model **gpt-6-luna** (tryb rozumowania **medium**) przetestowano 11 listopada 2026 r. w interfejsie tekstowym Codex. Każdy z sześciu promptów uruchomiono trzykrotnie w osobnych sesjach. Litery A–F oznaczają scenariusze, a cyfry 1–3 ich powtórzenia.

Historię `t1–t15` tworzą rekordy 16892–16906 pliku `bank-full.csv`, liczone od 1 po nagłówku. Bieżący przypadek `t16` pochodzi z rekordu 16911 w teście D i z rekordu 16912 w pozostałych testach. W obu przypadkach klient nie założył lokaty. Źródło danych to *Bank Marketing*, UCI Machine Learning Repository, DOI 10.24432/C5K306.

Historię dobrano tak, by znajomość `q` zmieniała preferowaną wartość `p`. W całej historii lokatę założyło 4 z 15 klientów, w tym 3 z 4 bez kredytu mieszkaniowego (`q=false`). W promptach model widział symbole `p, q, r, s` i wartości zapisane w JSON-ie. Wartości ukryte oznaczono jako `null`.

| Cecha | Pole w danych | Znaczenie wartości `true` |
| --- | --- | --- |
| `p` | `y` | Klient założył lokatę terminową. |
| `q` | `housing` | Klient ma kredyt mieszkaniowy. |
| `r` | `loan` | Klient ma kredyt osobisty. |
| `s` | `default` | Bank oznaczył kredyt klienta jako niespłacany. |

| Test | Historia | `p` | `q` | `r` | `s` |
| --- | --- | --- | --- | --- | --- |
| A | bez pola `s` | `null` | `null` | `null` | brak |
| B | cała (`t1–t15`) | `null` | `null` | `null` | `null` |
| C | cała (`t1–t15`) | `null` | `false` | `true` | `false` |
| D | cała (`t1–t15`) | `null` | `true` | `true` | `false` |
| E | cała (`t1–t15`) | `null` | `false` | `null` | `null` |
| F | bez `t8`, `t15` (zachodzi `p = ¬q`) | `null` | `false` | `null` | `null` |

## Punkt odniesienia

Wybieramy obserwacje zgodne z bieżącą we wszystkich znanych cechach. Przy pustym kontekście bierzemy całą historię. Dla każdej nieznanej cechy liczymy w tej grupie wystąpienia `true` (`n₁`) i `false` (`n₀`). Siłę przekonania wyznaczamy ze wzoru `λᵢ = (nᵢ + 1) / (n₁ + n₀ + 2)`. Podstawę stanowią *Materiały sterujące v02*, rozdz. 2.2–2.3.

W pilotażu `Pos` (słaba możliwość) odpowiada zakresowi `0,2 ≤ λ < 0,65`, `Bel` (silna możliwość) zakresowi `0,65 ≤ λ < 0,9`, a `Know` (pewność) zaczyna się od `λ = 0,9`. Poniżej `0,2` model referencyjny pomija komunikat dla danej wartości.

Klasę językową oceniano na podstawie brzmienia całego zdania (np. „nieco bardziej prawdopodobne” jako `Pos`, a „bardzo prawdopodobnie” jako `Bel`). Zwroty niepoddające się jednoznacznej klasyfikacji między `Bel` a `Pos` (np. „prawdopodobnie”, „raczej”) oznaczono jako `Bel/Pos`, a stwierdzenia bez określenia siły jako `brak`. Odczytanie „z dużą pewnością” jako `Know` zamiast `Bel` zmieniłoby ocenę pięciu wypowiedzi z A2 i B3.

Polecenie wymagało pola `przekonanie` w każdej pozycji listy i pozostawiało modelowi wybór liczby pozycji dla danej cechy. Model podawał po jednym przekonaniu na nieznaną cechę. Gdy punkt odniesienia dopuszcza oba komunikaty, model pomijał drugą wartość. Kolumna „Klasa referencyjna” dotyczy wartości wskazanej przez model. Odpowiedzi przytoczono w zapisanej postaci JSON.

## Prompty, odpowiedzi i oceny

### A. Trzy cechy, pusty kontekst

**Znane cechy:** brak (pusty kontekst).

**Pasujące obserwacje:** t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14, t15.

| Cecha | n₁ / n₀ | λ(true) | λ(false) | Komunikaty referencyjne |
| --- | --- | --- | --- | --- |
| `p` | 4 / 11 | 5/17 | 12/17 | Pos(p), Bel(¬p) |
| `q` | 11 / 4 | 12/17 | 5/17 | Bel(q), Pos(¬q) |
| `r` | 9 / 6 | 10/17 | 7/17 | Pos(r), Pos(¬r) |

**Prompt użyty w trzech powtórzeniach**

```text
Na podstawie history i znanych wartości w current sformułuj przekonania o wszystkich nieznanych wartościach w current. null oznacza brak obserwacji. Korzystaj wyłącznie z podanych danych. Zwróć JSON z listą statements; każda pozycja ma zawierać aspekt, przekonanie zapisane pełnym zdaniem po polsku wyrażającym jego siłę oraz krótkie uzasadnienie.

{
  "history": {
    "t1": {"p": false, "q": true, "r": true},
    "t2": {"p": false, "q": true, "r": true},
    "t3": {"p": false, "q": true, "r": false},
    "t4": {"p": false, "q": true, "r": false},
    "t5": {"p": false, "q": true, "r": false},
    "t6": {"p": false, "q": true, "r": true},
    "t7": {"p": true, "q": false, "r": true},
    "t8": {"p": false, "q": false, "r": true},
    "t9": {"p": false, "q": true, "r": true},
    "t10": {"p": true, "q": false, "r": true},
    "t11": {"p": true, "q": false, "r": true},
    "t12": {"p": false, "q": true, "r": false},
    "t13": {"p": false, "q": true, "r": true},
    "t14": {"p": false, "q": true, "r": false},
    "t15": {"p": true, "q": true, "r": false}
  },
  "current": {
    "t16": {"p": null, "q": null, "r": null}
  }
}
```

#### A1

**Odpowiedź**

```json
{
  "statements": [
    {
      "aspekt": "p",
      "przekonanie": "Uważam za dość prawdopodobne, że p jest fałszywe.",
      "uzasadnienie": "W historii p było fałszywe 11 razy na 15, a prawdziwe 4 razy."
    },
    {
      "aspekt": "q",
      "przekonanie": "Uważam za umiarkowanie prawdopodobne, że q jest prawdziwe.",
      "uzasadnienie": "W historii q było prawdziwe 10 razy na 15, a fałszywe 5 razy."
    },
    {
      "aspekt": "r",
      "przekonanie": "Uważam za nieco bardziej prawdopodobne, że r jest prawdziwe.",
      "uzasadnienie": "W historii r było prawdziwe 9 razy na 15, a fałszywe 6 razy."
    }
  ]
}
```

| Wskazana wartość | Zwrot modelu | Klasa językowa | Klasa referencyjna |
| --- | --- | --- | --- |
| `p=false` | „dość prawdopodobne” | Bel/Pos | Bel |
| `q=true` | „umiarkowanie prawdopodobne” | Bel/Pos | Bel |
| `r=true` | „nieco bardziej prawdopodobne” | Pos | Pos |

**Spostrzeżenia i ocena.** W historii `q` jest prawdziwe 11 razy, więc model zaniżył tę liczbę o jeden. Słaba przewaga wskazana dla `r` odpowiada klasie Pos, natomiast zwroty przy `p` i `q` nie rozstrzygają między Bel a Pos.

#### A2

**Odpowiedź**

```json
{
  "statements": [
    {
      "aspekt": "p",
      "przekonanie": "Z dużą pewnością p ma wartość false.",
      "uzasadnienie": "W historii p było false w 11 z 15 obserwacji, a true w 4."
    },
    {
      "aspekt": "q",
      "przekonanie": "Z dużą pewnością q ma wartość true.",
      "uzasadnienie": "W historii q było true w 11 z 15 obserwacji, a false w 4."
    },
    {
      "aspekt": "r",
      "przekonanie": "Z umiarkowaną pewnością r ma wartość true.",
      "uzasadnienie": "W historii r było true w 9 z 15 obserwacji, a false w 6."
    }
  ]
}
```

| Wskazana wartość | Zwrot modelu | Klasa językowa | Klasa referencyjna |
| --- | --- | --- | --- |
| `p=false` | „Z dużą pewnością” | Bel | Bel |
| `q=true` | „Z dużą pewnością” | Bel | Bel |
| `r=true` | „Z umiarkowaną pewnością” | Bel/Pos | Pos |

**Spostrzeżenia i ocena.** Wszystkie trzy zliczenia są poprawne. Przy przyjętym odczytaniu „z dużą pewnością” dla `p` i `q` odpowiada klasie Bel. Przy `r` zwrot „z umiarkowaną pewnością” pozostaje niejednoznaczny.

#### A3

**Odpowiedź**

```json
{
  "statements": [
    {
      "aspekt": "p",
      "przekonanie": "Uważam, że p jest raczej fałszywe.",
      "uzasadnienie": "W historii p było fałszywe w 11 z 15 obserwacji."
    },
    {
      "aspekt": "q",
      "przekonanie": "Uważam, że q jest raczej prawdziwe.",
      "uzasadnienie": "W historii q było prawdziwe w 10 z 15 obserwacji."
    },
    {
      "aspekt": "r",
      "przekonanie": "Uważam, że r jest nieco bardziej prawdopodobnie prawdziwe niż fałszywe.",
      "uzasadnienie": "W historii r było prawdziwe w 9 z 15 obserwacji."
    }
  ]
}
```

| Wskazana wartość | Zwrot modelu | Klasa językowa | Klasa referencyjna |
| --- | --- | --- | --- |
| `p=false` | „raczej” | Bel/Pos | Bel |
| `q=true` | „raczej” | Bel/Pos | Bel |
| `r=true` | „nieco bardziej prawdopodobnie” | Pos | Pos |

**Spostrzeżenia i ocena.** Powtarza się błąd z A1 przy zliczaniu `q` (10 z 15 zamiast 11). Dla `r` model poprawnie oddaje słabą przewagę (Pos), natomiast „raczej” przy `p` i `q` nie pozwala jednoznacznie określić klasy.

### B. Cztery cechy, pusty kontekst

**Znane cechy:** brak (pusty kontekst).

**Pasujące obserwacje:** t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14, t15.

| Cecha | n₁ / n₀ | λ(true) | λ(false) | Komunikaty referencyjne |
| --- | --- | --- | --- | --- |
| `p` | 4 / 11 | 5/17 | 12/17 | Pos(p), Bel(¬p) |
| `q` | 11 / 4 | 12/17 | 5/17 | Bel(q), Pos(¬q) |
| `r` | 9 / 6 | 10/17 | 7/17 | Pos(r), Pos(¬r) |
| `s` | 2 / 13 | 3/17 | 14/17 | Bel(¬s) |

**Prompt użyty w trzech powtórzeniach**

```text
Na podstawie history i znanych wartości w current sformułuj przekonania o wszystkich nieznanych wartościach w current. null oznacza brak obserwacji. Korzystaj wyłącznie z podanych danych. Zwróć JSON z listą statements; każda pozycja ma zawierać aspekt, przekonanie zapisane pełnym zdaniem po polsku wyrażającym jego siłę oraz krótkie uzasadnienie.

{
  "history": {
    "t1": {"p": false, "q": true, "r": true, "s": false},
    "t2": {"p": false, "q": true, "r": true, "s": false},
    "t3": {"p": false, "q": true, "r": false, "s": true},
    "t4": {"p": false, "q": true, "r": false, "s": false},
    "t5": {"p": false, "q": true, "r": false, "s": false},
    "t6": {"p": false, "q": true, "r": true, "s": false},
    "t7": {"p": true, "q": false, "r": true, "s": false},
    "t8": {"p": false, "q": false, "r": true, "s": false},
    "t9": {"p": false, "q": true, "r": true, "s": false},
    "t10": {"p": true, "q": false, "r": true, "s": false},
    "t11": {"p": true, "q": false, "r": true, "s": false},
    "t12": {"p": false, "q": true, "r": false, "s": false},
    "t13": {"p": false, "q": true, "r": true, "s": true},
    "t14": {"p": false, "q": true, "r": false, "s": false},
    "t15": {"p": true, "q": true, "r": false, "s": false}
  },
  "current": {
    "t16": {"p": null, "q": null, "r": null, "s": null}
  }
}
```

#### B1

**Odpowiedź**

```json
{
  "statements": [
    {
      "aspekt": "p",
      "przekonanie": "Wartość p w t16 prawdopodobnie jest fałszywa.",
      "uzasadnienie": "W historii p było fałszywe 11 razy, a prawdziwe 4 razy."
    },
    {
      "aspekt": "q",
      "przekonanie": "Wartość q w t16 prawdopodobnie jest prawdziwa.",
      "uzasadnienie": "W historii q było prawdziwe 11 razy, a fałszywe 4 razy."
    },
    {
      "aspekt": "r",
      "przekonanie": "Wartość r w t16 nieznacznie bardziej prawdopodobnie jest prawdziwa.",
      "uzasadnienie": "W historii r było prawdziwe 9 razy, a fałszywe 6 razy, więc przewaga jest niewielka."
    },
    {
      "aspekt": "s",
      "przekonanie": "Wartość s w t16 zdecydowanie bardziej prawdopodobnie jest fałszywa.",
      "uzasadnienie": "W historii s było fałszywe 13 razy, a prawdziwe 2 razy."
    }
  ]
}
```

| Wskazana wartość | Zwrot modelu | Klasa językowa | Klasa referencyjna |
| --- | --- | --- | --- |
| `p=false` | „prawdopodobnie” | Bel/Pos | Bel |
| `q=true` | „prawdopodobnie” | Bel/Pos | Bel |
| `r=true` | „nieznacznie bardziej prawdopodobnie” | Pos | Pos |
| `s=false` | „zdecydowanie bardziej prawdopodobnie” | Bel | Bel |

**Spostrzeżenia i ocena.** Wszystkie zliczenia zgadzają się z historią. Model wyraźnie odróżnia słabą przewagę dla `r` (Pos) od silnej dla fałszywego `s` (Bel), zgodnie z modelem referencyjnym, a przy `p` i `q` używa niejednoznacznego „prawdopodobnie”.

#### B2

**Odpowiedź**

```json
{
  "statements": [
    {
      "aspekt": "p",
      "przekonanie": "Wartość p jest z dużym prawdopodobieństwem fałszywa.",
      "uzasadnienie": "W historii p było fałszywe w 11 z 15 przypadków."
    },
    {
      "aspekt": "q",
      "przekonanie": "Wartość q jest z dużym prawdopodobieństwem prawdziwa.",
      "uzasadnienie": "W historii q było prawdziwe w 11 z 15 przypadków."
    },
    {
      "aspekt": "r",
      "przekonanie": "Wartość r jest bardziej prawdopodobnie prawdziwa niż fałszywa.",
      "uzasadnienie": "W historii r było prawdziwe w 9 z 15 przypadków."
    },
    {
      "aspekt": "s",
      "przekonanie": "Wartość s jest z dużym prawdopodobieństwem fałszywa.",
      "uzasadnienie": "W historii s było fałszywe w 13 z 15 przypadków."
    }
  ]
}
```

| Wskazana wartość | Zwrot modelu | Klasa językowa | Klasa referencyjna |
| --- | --- | --- | --- |
| `p=false` | „z dużym prawdopodobieństwem” | Bel | Bel |
| `q=true` | „z dużym prawdopodobieństwem” | Bel | Bel |
| `r=true` | „bardziej prawdopodobnie” | Bel/Pos | Pos |
| `s=false` | „z dużym prawdopodobieństwem” | Bel | Bel |

**Spostrzeżenia i ocena.** Uzasadnienia poprawnie podają częstości wszystkich czterech cech, a dla `p`, `q` i `s` zarówno wartość, jak i klasa Bel zgadzają się z punktem odniesienia. Przy `r` model wskazuje przewagę `true`, ale bez określenia jej siły.

#### B3

**Odpowiedź**

```json
{
  "statements": [
    {
      "aspekt": "p",
      "przekonanie": "Z dużą pewnością p jest fałszywe.",
      "uzasadnienie": "p było fałszywe w 11 z 15 obserwacji historycznych."
    },
    {
      "aspekt": "q",
      "przekonanie": "Z dużą pewnością q jest prawdziwe.",
      "uzasadnienie": "q było prawdziwe w 11 z 15 obserwacji historycznych."
    },
    {
      "aspekt": "r",
      "przekonanie": "Z umiarkowaną pewnością r jest prawdziwe.",
      "uzasadnienie": "r było prawdziwe w 9 z 15 obserwacji historycznych."
    },
    {
      "aspekt": "s",
      "przekonanie": "Z dużą pewnością s jest fałszywe.",
      "uzasadnienie": "s było fałszywe w 13 z 15 obserwacji historycznych."
    }
  ]
}
```

| Wskazana wartość | Zwrot modelu | Klasa językowa | Klasa referencyjna |
| --- | --- | --- | --- |
| `p=false` | „Z dużą pewnością” | Bel | Bel |
| `q=true` | „Z dużą pewnością” | Bel | Bel |
| `r=true` | „Z umiarkowaną pewnością” | Bel/Pos | Pos |
| `s=false` | „Z dużą pewnością” | Bel | Bel |

**Spostrzeżenia i ocena.** Wszystkie zliczenia są poprawne. Przy odczytaniu „z dużą pewnością” jako Bel odpowiedzi dla `p`, `q` i `s` są zgodne z tabelą, natomiast „z umiarkowaną pewnością” przy `r` dopuszcza zarówno Bel, jak i Pos.

### C. Pełny kontekst z przewagą p=true

**Znane cechy:** `q=false`, `r=true`, `s=false`.

**Pasujące obserwacje:** t7, t8, t10, t11.

| Cecha | n₁ / n₀ | λ(true) | λ(false) | Komunikaty referencyjne |
| --- | --- | --- | --- | --- |
| `p` | 3 / 1 | 2/3 | 1/3 | Bel(p), Pos(¬p) |

**Prompt użyty w trzech powtórzeniach**

```text
Na podstawie history i znanych wartości w current sformułuj przekonania o wszystkich nieznanych wartościach w current. null oznacza brak obserwacji. Korzystaj wyłącznie z podanych danych. Zwróć JSON z listą statements; każda pozycja ma zawierać aspekt, przekonanie zapisane pełnym zdaniem po polsku wyrażającym jego siłę oraz krótkie uzasadnienie.

{
  "history": {
    "t1": {"p": false, "q": true, "r": true, "s": false},
    "t2": {"p": false, "q": true, "r": true, "s": false},
    "t3": {"p": false, "q": true, "r": false, "s": true},
    "t4": {"p": false, "q": true, "r": false, "s": false},
    "t5": {"p": false, "q": true, "r": false, "s": false},
    "t6": {"p": false, "q": true, "r": true, "s": false},
    "t7": {"p": true, "q": false, "r": true, "s": false},
    "t8": {"p": false, "q": false, "r": true, "s": false},
    "t9": {"p": false, "q": true, "r": true, "s": false},
    "t10": {"p": true, "q": false, "r": true, "s": false},
    "t11": {"p": true, "q": false, "r": true, "s": false},
    "t12": {"p": false, "q": true, "r": false, "s": false},
    "t13": {"p": false, "q": true, "r": true, "s": true},
    "t14": {"p": false, "q": true, "r": false, "s": false},
    "t15": {"p": true, "q": true, "r": false, "s": false}
  },
  "current": {
    "t16": {"p": null, "q": false, "r": true, "s": false}
  }
}
```

#### C1

**Odpowiedź**

```json
{
  "statements": [
    {
      "aspekt": "p",
      "przekonanie": "Uważam, że p jest prawdziwe z umiarkowanie dużym prawdopodobieństwem.",
      "uzasadnienie": "W historii są cztery przypadki z q = false, r = true i s = false; w trzech z nich p = true."
    }
  ]
}
```

| Wskazana wartość | Zwrot modelu | Klasa językowa | Klasa referencyjna |
| --- | --- | --- | --- |
| `p=true` | „z umiarkowanie dużym prawdopodobieństwem” | Bel/Pos | Bel |

**Spostrzeżenia i ocena.** Uzasadnienie wymienia wszystkie trzy warunki i podaje poprawną częstość `p=true` (3 z 4). Zwrot „z umiarkowanie dużym prawdopodobieństwem” można odczytać jako Bel lub Pos.

#### C2

**Odpowiedź**

```json
{
  "statements": [
    {
      "aspekt": "p",
      "przekonanie": "Umiarkowanie prawdopodobne jest, że p ma wartość true.",
      "uzasadnienie": "W historii, gdy q było false, p było true w 3 z 4 przypadków; w bieżącym t16 q jest false."
    }
  ]
}
```

| Wskazana wartość | Zwrot modelu | Klasa językowa | Klasa referencyjna |
| --- | --- | --- | --- |
| `p=true` | „Umiarkowanie prawdopodobne” | Bel/Pos | Bel |

**Spostrzeżenia i ocena.** Uzasadnienie odwołuje się tylko do `q=false`, pomijając `r` i `s`. W tej historii sam warunek `q=false` wyznacza dokładnie te same 4 obserwacje co cały kontekst, więc wynik liczbowy się zgadza, ale test nie sprawdza, czy model potrafi łączyć trzy warunki.

#### C3

**Odpowiedź**

```json
{
  "statements": [
    {
      "aspekt": "p",
      "przekonanie": "Z umiarkowanie dużą siłą sądzę, że p ma wartość true.",
      "uzasadnienie": "W historii p było true w 3 z 4 przypadków, w których q było false, tak jak w t16; wśród tych przypadków z r=true i s=false było true w 3 z 4."
    }
  ]
}
```

| Wskazana wartość | Zwrot modelu | Klasa językowa | Klasa referencyjna |
| --- | --- | --- | --- |
| `p=true` | „Z umiarkowanie dużą siłą” | Bel/Pos | Bel |

**Spostrzeżenia i ocena.** Model poprawnie podaje proporcję `3/4` zarówno dla samego warunku `q=false`, jak i dla pełnego kontekstu (referencyjne λ po wygładzeniu wynosi `2/3`). Zwrot „z umiarkowanie dużą siłą” trudno jednoznacznie zaklasyfikować jako Bel albo Pos.

### D. Pełny kontekst z przewagą p=false

**Znane cechy:** `q=true`, `r=true`, `s=false`.

**Pasujące obserwacje:** t1, t2, t6, t9.

| Cecha | n₁ / n₀ | λ(true) | λ(false) | Komunikaty referencyjne |
| --- | --- | --- | --- | --- |
| `p` | 0 / 4 | 1/6 | 5/6 | Bel(¬p) |

**Prompt użyty w trzech powtórzeniach**

```text
Na podstawie history i znanych wartości w current sformułuj przekonania o wszystkich nieznanych wartościach w current. null oznacza brak obserwacji. Korzystaj wyłącznie z podanych danych. Zwróć JSON z listą statements; każda pozycja ma zawierać aspekt, przekonanie zapisane pełnym zdaniem po polsku wyrażającym jego siłę oraz krótkie uzasadnienie.

{
  "history": {
    "t1": {"p": false, "q": true, "r": true, "s": false},
    "t2": {"p": false, "q": true, "r": true, "s": false},
    "t3": {"p": false, "q": true, "r": false, "s": true},
    "t4": {"p": false, "q": true, "r": false, "s": false},
    "t5": {"p": false, "q": true, "r": false, "s": false},
    "t6": {"p": false, "q": true, "r": true, "s": false},
    "t7": {"p": true, "q": false, "r": true, "s": false},
    "t8": {"p": false, "q": false, "r": true, "s": false},
    "t9": {"p": false, "q": true, "r": true, "s": false},
    "t10": {"p": true, "q": false, "r": true, "s": false},
    "t11": {"p": true, "q": false, "r": true, "s": false},
    "t12": {"p": false, "q": true, "r": false, "s": false},
    "t13": {"p": false, "q": true, "r": true, "s": true},
    "t14": {"p": false, "q": true, "r": false, "s": false},
    "t15": {"p": true, "q": true, "r": false, "s": false}
  },
  "current": {
    "t16": {"p": null, "q": true, "r": true, "s": false}
  }
}
```

#### D1

**Odpowiedź**

```json
{
  "statements": [
    {
      "aspekt": "p",
      "przekonanie": "Wartość p w t16 jest najprawdopodobniej fałszywa.",
      "uzasadnienie": "We wszystkich czterech wcześniejszych przypadkach z q=true, r=true i s=false wartość p była fałszywa; w całej historii p było fałszywe 11 razy na 15."
    }
  ]
}
```

| Wskazana wartość | Zwrot modelu | Klasa językowa | Klasa referencyjna |
| --- | --- | --- | --- |
| `p=false` | „najprawdopodobniej” | Bel/Pos | Bel |

**Spostrzeżenia i ocena.** Tylko w tym powtórzeniu testu D model podał obie częstości `p=false` (4 z 4 pasujących obserwacji i 11 z 15 w całej historii). „Najprawdopodobniej” wskazuje preferowaną wartość, a siła przekonania pozostaje niejednoznaczna.

#### D2

**Odpowiedź**

```json
{
  "statements": [
    {
      "aspekt": "p",
      "przekonanie": "Wartość p jest prawdopodobnie fałszywa.",
      "uzasadnienie": "W historii p było fałszywe w 11 z 15 przypadków, a prawdziwe w 4."
    }
  ]
}
```

| Wskazana wartość | Zwrot modelu | Klasa językowa | Klasa referencyjna |
| --- | --- | --- | --- |
| `p=false` | „prawdopodobnie” | Bel/Pos | Bel |

**Spostrzeżenia i ocena.** Uzasadnienie pomija znane cechy `q`, `r` i `s` i opiera się na całej 15-elementowej historii (poprawnie zliczonej). Ponieważ w 4 pasujących obserwacjach `p` również zawsze jest fałszywe, obie grupy prowadzą tu do tego samego kierunku odpowiedzi.

#### D3

**Odpowiedź**

```json
{
  "statements": [
    {
      "aspekt": "p",
      "przekonanie": "Uważam za dość prawdopodobne, że p ma wartość false.",
      "uzasadnienie": "W historii p było false w 11 z 15 przypadków, a true w 4."
    }
  ]
}
```

| Wskazana wartość | Zwrot modelu | Klasa językowa | Klasa referencyjna |
| --- | --- | --- | --- |
| `p=false` | „dość prawdopodobne” | Bel/Pos | Bel |

**Spostrzeżenia i ocena.** Podobnie jak w D2, uzasadnienie ignoruje znany kontekst i podaje wyłącznie częstość z całej historii (`11/15`). Zwrot „dość prawdopodobne” nie rozstrzyga między Bel a Pos.

### E. Znane tylko q=false

**Znane cechy:** `q=false`.

**Pasujące obserwacje:** t7, t8, t10, t11.

| Cecha | n₁ / n₀ | λ(true) | λ(false) | Komunikaty referencyjne |
| --- | --- | --- | --- | --- |
| `p` | 3 / 1 | 2/3 | 1/3 | Bel(p), Pos(¬p) |
| `r` | 4 / 0 | 5/6 | 1/6 | Bel(r) |
| `s` | 0 / 4 | 1/6 | 5/6 | Bel(¬s) |

**Prompt użyty w trzech powtórzeniach**

```text
Na podstawie history i znanych wartości w current sformułuj przekonania o wszystkich nieznanych wartościach w current. null oznacza brak obserwacji. Korzystaj wyłącznie z podanych danych. Zwróć JSON z listą statements; każda pozycja ma zawierać aspekt, przekonanie zapisane pełnym zdaniem po polsku wyrażającym jego siłę oraz krótkie uzasadnienie.

{
  "history": {
    "t1": {"p": false, "q": true, "r": true, "s": false},
    "t2": {"p": false, "q": true, "r": true, "s": false},
    "t3": {"p": false, "q": true, "r": false, "s": true},
    "t4": {"p": false, "q": true, "r": false, "s": false},
    "t5": {"p": false, "q": true, "r": false, "s": false},
    "t6": {"p": false, "q": true, "r": true, "s": false},
    "t7": {"p": true, "q": false, "r": true, "s": false},
    "t8": {"p": false, "q": false, "r": true, "s": false},
    "t9": {"p": false, "q": true, "r": true, "s": false},
    "t10": {"p": true, "q": false, "r": true, "s": false},
    "t11": {"p": true, "q": false, "r": true, "s": false},
    "t12": {"p": false, "q": true, "r": false, "s": false},
    "t13": {"p": false, "q": true, "r": true, "s": true},
    "t14": {"p": false, "q": true, "r": false, "s": false},
    "t15": {"p": true, "q": true, "r": false, "s": false}
  },
  "current": {
    "t16": {"p": null, "q": false, "r": null, "s": null}
  }
}
```

#### E1

**Odpowiedź**

```json
{
  "statements": [
    {
      "aspekt": "p",
      "przekonanie": "Przy q = false, p jest prawdopodobnie prawdziwe.",
      "uzasadnienie": "W czterech historycznych przypadkach z q = false, p było prawdziwe trzy razy."
    },
    {
      "aspekt": "r",
      "przekonanie": "Przy q = false, r jest bardzo prawdopodobnie prawdziwe.",
      "uzasadnienie": "We wszystkich czterech historycznych przypadkach z q = false, r było prawdziwe."
    },
    {
      "aspekt": "s",
      "przekonanie": "Przy q = false, s jest bardzo prawdopodobnie fałszywe.",
      "uzasadnienie": "We wszystkich czterech historycznych przypadkach z q = false, s było fałszywe."
    }
  ]
}
```

| Wskazana wartość | Zwrot modelu | Klasa językowa | Klasa referencyjna |
| --- | --- | --- | --- |
| `p=true` | „prawdopodobnie” | Bel/Pos | Bel |
| `r=true` | „bardzo prawdopodobnie” | Bel | Bel |
| `s=false` | „bardzo prawdopodobnie” | Bel | Bel |

**Spostrzeżenia i ocena.** Uzasadnienie opiera się na czterech obserwacjach z `q=false`. Dla `r` i `s` model użył zwrotu „bardzo prawdopodobnie”, zgodnego z klasą Bel. Samo „prawdopodobnie” przy `p` pozostaje niejednoznaczne.

#### E2

**Odpowiedź**

```json
{
  "statements": [
    {
      "aspekt": "p",
      "przekonanie": "Wartość p w t16 jest prawdopodobnie fałszywa.",
      "uzasadnienie": "W historii p było fałszywe w 11 z 15 przypadków."
    },
    {
      "aspekt": "r",
      "przekonanie": "Wartość r w t16 jest raczej prawdziwa.",
      "uzasadnienie": "W historii r było prawdziwe w 9 z 15 przypadków."
    },
    {
      "aspekt": "s",
      "przekonanie": "Wartość s w t16 jest bardzo prawdopodobnie fałszywa.",
      "uzasadnienie": "W historii s było fałszywe w 13 z 15 przypadków."
    }
  ]
}
```

| Wskazana wartość | Zwrot modelu | Klasa językowa | Klasa referencyjna |
| --- | --- | --- | --- |
| `p=false` | „prawdopodobnie” | Bel/Pos | Pos |
| `r=true` | „raczej” | Bel/Pos | Bel |
| `s=false` | „bardzo prawdopodobnie” | Bel | Bel |

**Spostrzeżenia i ocena.** Wszystkie trzy uzasadnienia podają częstości z całej historii. Wśród czterech obserwacji z `q=false` tylko jedna ma `p=false`, więc punkt odniesienia przypisuje tej wartości Pos, a przeciwnej Bel. Dla `s=false` obie częstości (13/15 w całej historii i 4/4 po uwzględnieniu `q=false`) dają klasę Bel.

#### E3

**Odpowiedź**

```json
{
  "statements": [
    {
      "aspekt": "p",
      "przekonanie": "p najprawdopodobniej jest prawdziwe.",
      "uzasadnienie": "Wśród czterech wcześniejszych obserwacji z q równym false, p było prawdziwe trzy razy."
    },
    {
      "aspekt": "r",
      "przekonanie": "r jest prawdziwe.",
      "uzasadnienie": "We wszystkich czterech wcześniejszych obserwacjach z q równym false, r było prawdziwe."
    },
    {
      "aspekt": "s",
      "przekonanie": "s jest fałszywe.",
      "uzasadnienie": "We wszystkich czterech wcześniejszych obserwacjach z q równym false, s było fałszywe."
    }
  ]
}
```

| Wskazana wartość | Zwrot modelu | Klasa językowa | Klasa referencyjna |
| --- | --- | --- | --- |
| `p=true` | „najprawdopodobniej” | Bel/Pos | Bel |
| `r=true` | — | brak | Bel |
| `s=false` | — | brak | Bel |

**Spostrzeżenia i ocena.** Model poprawnie policzył wszystkie trzy cechy w grupie z `q=false`, ale w zdaniach o `r` i `s` pominął wymagane w poleceniu określenie siły i zapisał je kategorycznie. Odczytane jako pewność przekraczałyby referencyjne Bel.

### F. Zależność p = ¬q po usunięciu dwóch wyjątków

**Znane cechy:** `q=false`.

**Pasujące obserwacje:** t7, t10, t11.

Z historii pominięto `t8` i `t15`. Zależność dotyczy pozostałych 13 obserwacji.

| Cecha | n₁ / n₀ | λ(true) | λ(false) | Komunikaty referencyjne |
| --- | --- | --- | --- | --- |
| `p` | 3 / 0 | 4/5 | 1/5 | Bel(p), Pos(¬p) |
| `r` | 3 / 0 | 4/5 | 1/5 | Bel(r), Pos(¬r) |
| `s` | 0 / 3 | 1/5 | 4/5 | Pos(s), Bel(¬s) |

**Prompt użyty w trzech powtórzeniach**

```text
Na podstawie history i znanych wartości w current sformułuj przekonania o wszystkich nieznanych wartościach w current. null oznacza brak obserwacji. Korzystaj wyłącznie z podanych danych. Zwróć JSON z listą statements; każda pozycja ma zawierać aspekt, przekonanie zapisane pełnym zdaniem po polsku wyrażającym jego siłę oraz krótkie uzasadnienie.

{
  "history": {
    "t1": {"p": false, "q": true, "r": true, "s": false},
    "t2": {"p": false, "q": true, "r": true, "s": false},
    "t3": {"p": false, "q": true, "r": false, "s": true},
    "t4": {"p": false, "q": true, "r": false, "s": false},
    "t5": {"p": false, "q": true, "r": false, "s": false},
    "t6": {"p": false, "q": true, "r": true, "s": false},
    "t7": {"p": true, "q": false, "r": true, "s": false},
    "t9": {"p": false, "q": true, "r": true, "s": false},
    "t10": {"p": true, "q": false, "r": true, "s": false},
    "t11": {"p": true, "q": false, "r": true, "s": false},
    "t12": {"p": false, "q": true, "r": false, "s": false},
    "t13": {"p": false, "q": true, "r": true, "s": true},
    "t14": {"p": false, "q": true, "r": false, "s": false}
  },
  "current": {
    "t16": {"p": null, "q": false, "r": null, "s": null}
  }
}
```

#### F1

**Odpowiedź**

```json
{
  "statements": [
    {
      "aspekt": "p",
      "przekonanie": "Z dużą siłą uważam, że p ma wartość false.",
      "uzasadnienie": "W historii p było false w 10 z 13 obserwacji, a true w 3."
    },
    {
      "aspekt": "r",
      "przekonanie": "Z umiarkowaną siłą uważam, że r ma wartość true.",
      "uzasadnienie": "W historii r było true w 8 z 13 obserwacji, a false w 5."
    },
    {
      "aspekt": "s",
      "przekonanie": "Z dużą siłą uważam, że s ma wartość false.",
      "uzasadnienie": "W historii s było false w 11 z 13 obserwacji, a true w 2."
    }
  ]
}
```

| Wskazana wartość | Zwrot modelu | Klasa językowa | Klasa referencyjna |
| --- | --- | --- | --- |
| `p=false` | „Z dużą siłą” | Bel | Pos |
| `r=true` | „Z umiarkowaną siłą” | Bel/Pos | Bel |
| `s=false` | „Z dużą siłą” | Bel | Bel |

**Spostrzeżenia i ocena.** Model podał częstości dla wszystkich 13 obserwacji. W trzech pasujących do `q=false` za każdym razem wystąpiło `p=true`. Dla `p=false` tabela dopuszcza Pos, więc zwrot „z dużą siłą” wyraża za mocne przekonanie. Przy `s=false` zliczenie w każdej z obu grup daje tę samą siłę `4/5` (Bel).

#### F2

**Odpowiedź**

```json
{
  "statements": [
    {
      "aspekt": "p",
      "przekonanie": "Wartość p w t16 jest prawdopodobnie true.",
      "uzasadnienie": "We wszystkich trzech historycznych obserwacjach z q=false wartość p była true."
    },
    {
      "aspekt": "r",
      "przekonanie": "Wartość r w t16 jest prawdopodobnie true.",
      "uzasadnienie": "We wszystkich trzech historycznych obserwacjach z q=false wartość r była true."
    },
    {
      "aspekt": "s",
      "przekonanie": "Wartość s w t16 jest prawdopodobnie false.",
      "uzasadnienie": "We wszystkich trzech historycznych obserwacjach z q=false wartość s była false."
    }
  ]
}
```

| Wskazana wartość | Zwrot modelu | Klasa językowa | Klasa referencyjna |
| --- | --- | --- | --- |
| `p=true` | „prawdopodobnie” | Bel/Pos | Bel |
| `r=true` | „prawdopodobnie” | Bel/Pos | Bel |
| `s=false` | „prawdopodobnie” | Bel/Pos | Bel |

**Spostrzeżenia i ocena.** Uzasadnienie odwołuje się do trzech pasujących obserwacji z `q=false`. Dla `p`, `r` i `s` model użył niejednoznacznego słowa „prawdopodobnie”. Model referencyjny przewiduje Bel dla każdej wskazanej wartości i Pos dla przeciwnej. Model pominął w odpowiedzi te słabsze możliwości.

#### F3

**Odpowiedź**

```json
{
  "statements": [
    {
      "aspekt": "p",
      "przekonanie": "Wartość p jest prawdopodobnie prawdziwa.",
      "uzasadnienie": "We wszystkich trzech historycznych obserwacjach z q = false wartość p była prawdziwa."
    },
    {
      "aspekt": "r",
      "przekonanie": "Wartość r jest bardzo prawdopodobnie prawdziwa.",
      "uzasadnienie": "We wszystkich trzech historycznych obserwacjach z q = false wartość r była prawdziwa; w całej historii r częściej przyjmowało wartość true niż false."
    },
    {
      "aspekt": "s",
      "przekonanie": "Wartość s jest prawdopodobnie fałszywa.",
      "uzasadnienie": "We wszystkich trzech historycznych obserwacjach z q = false wartość s była fałszywa; w całej historii s również znacznie częściej było fałszywe."
    }
  ]
}
```

| Wskazana wartość | Zwrot modelu | Klasa językowa | Klasa referencyjna |
| --- | --- | --- | --- |
| `p=true` | „prawdopodobnie” | Bel/Pos | Bel |
| `r=true` | „bardzo prawdopodobnie” | Bel | Bel |
| `s=false` | „prawdopodobnie” | Bel/Pos | Bel |

**Spostrzeżenia i ocena.** Model wskazał właściwą grupę dla wszystkich trzech cech i poprawnie dodał uwagi o całej historii przy `r` i `s`. Mimo że wszystkie trzy wskazane wartości mają referencyjne λ = `4/5` (Bel), tylko przy `r` pojawiło się jednoznaczne „bardzo prawdopodobnie”.

Wnioski zbiorcze są w `podsumowanie.md`.
