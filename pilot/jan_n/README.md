# Pilot – Jan N.

## System (krok 1)

| | |
|---|---|
| Modele | **Bielik-11B-v3.1-Instruct** (SpeakLeash / ACK Cyfronet AGH), id `arklabsai/Bielik-11B-v3.1-Instruct`; **Qwen3.6-35B-A3B** (Alibaba, MoE 35B / 3B aktywnych), id `arklabsai/Qwen3.6-35B-A3B`; **Qwen3.5-122B-A10B** (Alibaba, MoE 122B / 10B aktywnych), id `arklabsai/Qwen3.5-122B-A10B` |
| Dostawca / interfejs | ark-labs.cloud, API zgodne z OpenAI (`POST /api/v1/chat/completions`) |
| Data testów | 2026-11-26 |
| Parametry | `temperature=0.7`; `max_tokens=2048` (Bielik) / `16384` (oba Qwen); pozostałe domyślne; 1 wiadomość `user` na sesję, bez system promptu |
| Język promptów | polski |

Uwagi techniczne:
- Dla Bielika dostawca **dokleja własny system prompt** (~1100 tokenów: `prompt_tokens` ≈ 1460 vs ≈ 360 dla Qwenów przy tym samym prompcie). Nie mamy na niego wpływu – to część badanego „systemu”. Oba Qwen dostają wyłącznie nasz prompt.
- Endpoint udostępnia tylko wersję v3.1 (v3.0 zwraca `model_not_found`).
- Oba modele mają flagę `ark_reasoning: true`, ale we wszystkich odpowiedziach `reasoning_tokens = 0` – oba Qwen „rozumują na głos” w treści odpowiedzi.

## Interpretacja dziedzinowa (krok 1a)

Przebiegi potoku CI dla commitów w repozytorium:

`Aspekty = {p: build zakończył się niepowodzeniem, q: commit zmienia zależności projektu, r: commit dotyczy wyłącznie dokumentacji, s: commit wypchnięty w piątek po południu}`

Interpretacja jest spójna z KB (np. klasa r=1 → zawsze p=0: commity „tylko dokumentacja” nie psują buildu), więc wiedza dziedzinowa i dane wskazują ten sam kierunek w T2/D2 – przy „zaciąganiu” wiedzy spodziewalibyśmy się raczej *większej* pewności ¬p w D2.

## Pliki

| plik | zawartość |
|---|---|
| `kb.csv` | KB(t_teraz − 1), N = 12 |
| `contexts.yaml` | testy T1–T5 |
| `prompt_template.txt` / `prompt_template_domain.txt` | szablon symboliczny / dziedzinowy |
| `reference.py` | klasa warunkowa, holon, progi 0.2 / 0.65 / 0.9 (`python3 reference.py` = self-test z tabelą z `pilot_README §4`) |
| `run.py` | wysyła prompty, zapisuje `results/<model>/<data>.jsonl` |
| `analysis/<model>.yaml` | wstępna klasyfikacja fraz i ocena (propozycja LLM – do weryfikacji) |
| `report.py` | składa `report/<model>.md` (format z `pilot_README §6`) |
| `podsumowanie.md` | podsumowanie indywidualne (krok 5) |

## Uruchomienie

```bash
ENV=../../../hacknation/cyfryzacja-formularzy/.env   # LLM_REMOTE_BASE_URL / LLM_REMOTE_API_KEY
M=arklabsai/Bielik-11B-v3.1-Instruct
uv run run.py --env-file $ENV --model $M --repeats 3                    # T1–T5 ×3
uv run run.py --env-file $ENV --model $M --repeats 3 --variant domain   # D1–D5 ×3
uv run run.py --env-file $ENV --model $M --all-contexts                 # 27 kontekstów ×1
uv run report.py arklabsai__Bielik-11B-v3.1-Instruct
# Qwen: M=arklabsai/Qwen3.5-122B-A10B lub arklabsai/Qwen3.6-35B-A3B i dodatkowo --max-tokens 16384
```

Inny model (np. lokalny serwer OpenAI-compatible): `uv run run.py --base-url http://127.0.0.1:8080/v1 --model <id> …` (klucz z `LLM_API_KEY`).
