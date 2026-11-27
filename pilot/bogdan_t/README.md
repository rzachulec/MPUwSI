# Pilotaż – Bohdan Tkachenko

## Badanie na danych bankowych

Model `gpt-6-luna` testowano w trybie `medium`. Odpowiedzi zebrano 11 listopada 2026 r. w 18 osobnych sesjach tekstowych. Temperatura pozostaje nieustalona.

W zbiorze *Bank Marketing* (UCI Machine Learning Repository, DOI 10.24432/C5K306) `p` oznacza założenie lokaty terminowej, `q` posiadanie kredytu mieszkaniowego, `r` posiadanie kredytu osobistego, a `s` kredyt oznaczony przez bank jako niespłacany. W promptach cechy występują jako symbole.

`report/gpt-6-luna.md` zawiera prompty A–F, zapisane odpowiedzi i ich ocenę. `podsumowanie.md` zawiera wnioski, a `analiza_pilotazowa.pdf` sprawozdanie do druku. `results/gpt-6-luna/2026-11-11.jsonl` zawiera te same 18 prób. W polu `timestamp` podano datę znaną z zapisu. Pole `response` zawiera pełną zapisaną odpowiedź JSON jako tekst.

## Próby API na danych kursowych

`kb.csv` zawiera 12 obserwacji z instrukcji repozytorium. `contexts.yaml` definiuje testy T1–T5. `null` oznacza nieznaną cechę, która pojawia się w prompcie jako `?`. Stała część polecenia jest w `prompt_template.txt`. `reference.py` liczy na ułamkach, stosując pilotażowe progi 0,2, 0,65 i 0,9.

Poniższe polecenia uruchom w PowerShellu z katalogu `pilot/bogdan_t`. Potrzebny jest Python 3.10 lub nowszy.

~~~powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m unittest -v
.\.venv\Scripts\python run.py --dry-run
~~~

Do wywołania API ustaw klucz dostawcy w środowisku albo w lokalnym `.env`. Zmienna `PILOT_MODEL` w poniższym przykładzie powinna zawierać identyfikator `dostawca/model` obsługiwany przez LiteLLM.

~~~powershell
.\.venv\Scripts\python run.py --model $env:PILOT_MODEL --repeats 3
~~~

Opcja `--test T2` ogranicza serię do jednej próby kontrolnej. `--temperature` podaje temperaturę dostawcy. Przy pominięciu tej opcji skrypt zapisuje `null` w metadanych, a dostawca stosuje wartość domyślną.

Każde wywołanie otrzymuje jedną wiadomość użytkownika. Skrypt dopisuje odpowiedzi do `results/<model>/<data UTC>.jsonl` oraz tworzy lub uzupełnia szkielet `report/<model>.md`. W ścieżce ukośnik z identyfikatora modelu zapisuje się jako `%2F`. Każdy wpis zawiera treść odpowiedzi z API, wersję zwróconą przez dostawcę i wynik referencyjny. Klasyfikację fraz i ocenę odpowiedzi uzupełnia autor pilotażu.

Seria T1–T5 ma przygotowane dane, referencje i testy skryptu. Wyniki w archiwum pochodzą z bankowego pilotażu A–F.
