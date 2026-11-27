# Pilotaż – Bohdan Tkachenko

**Model:** `gpt-6-luna` (Codex, tryb rozumowania `medium`, 11.11.2026). Sześć scenariuszy (A–F), po trzy powtórzenia w osobnych sesjach, na 15 rekordach ze zbioru UCI *Bank Marketing* zakodowanych symbolicznie jako `p, q, r, s`.

- Przy pustym kontekście (A i B) model w każdej z sześciu prób wskazał te same wartości cech `p`, `q` i `r`. W A1 i A3 podał 10 wystąpień `q=true` zamiast 11.
- Przy znanych cechach (C–F) w 8 z 12 prób model oparł uzasadnienie na pasujących obserwacjach, a w 4 (D2, D3, E2, F1) policzył wyłącznie częstości z całej historii. W D nie zmieniło to wniosku o `p`, natomiast w E2 i F1 doprowadziło do przeciwnego wskazania niż wynika z klasy warunkowej.
- W F1 odpowiedź `p=false` zgadzała się z decyzją klienta zapisaną w zbiorze. Model podał częstość z całej historii. Każdy z trzech klientów spełniających warunek `q=false` założył lokatę. W F2 i F3 uzasadnienie uwzględnia te trzy obserwacje. Próby F obejmują tylko jedną wartość `q`, więc nie rozstrzygają, czy model zauważył regułę `p = ¬q` w całym zbiorze.
- Spośród 45 wypowiedzi 15 zaliczono do `Bel`, 3 do `Pos`, a 25 oznaczono jako `Bel/Pos` z powodu niejednoznacznego sformułowania. Dwie kategoryczne odpowiedzi w E3, dotyczące `r` i `s`, pomijały określenie siły.
- Przy przyjętej klasyfikacji 17 z 18 wypowiedzi oznaczonych jako `Bel` lub `Pos` miało siłę dopuszczoną dla wskazanej wartości. Do tych 17 należą wypowiedzi o `s` w E2 i F1, chociaż model uzasadnił je częstościami z całej historii. Dla `p=false` w F1 użył `Bel`, a punkt odniesienia dopuszczał `Pos`.
- W każdym scenariuszu były pasujące obserwacje, a dla każdej testowanej cechy jedna wartość przeważała. Najwyższa siła referencyjna wyniosła `5/6`, poniżej progu `Know`.

Prompty, odpowiedzi i oceny są w `report/gpt-6-luna.md`. Wersja do druku to `analiza_pilotazowa.pdf`.
