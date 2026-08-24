# Projekt Badawczy

Plik zawiera opis odtworzenia wyników oraz kolejność uruchamiania skryptów wraz z opisem przetwarzanych danych.

### **Krok 0: Pobranie i podział danych wejściowych**
1. Pobierz dane z bazy **AIDEV** (https://huggingface.co/datasets/hao-li/AIDev/viewer/issue).
2. Wyciągnij listę wszystkich użytkowników za pomocą zapytania SQL:
   ```sql
   SELECT login FROM all_user
   ```
3. Wynik zapytania zapisz do pliku CSV **bez wiersza nagłówkowego** (skrypty w kroku 1 wczytują pliki
   zakładając brak nagłówka).
4. Podziel plik na mniejsze części (po 100 loginów na plik), nazwij je kolejnymi liczbami
   (`1.csv`, `2.csv`, ...) i umieść je w folderze `data/input/`.

### **Krok 1: Pobranie dodatkowych metryk z GitHub API**
Wszystkie niezbędne skrypty znajdziesz w folderze `scripts/prepare_data`.

1. W `download_from_github.py` uzupełnij `GITHUB_TOKEN`.
2. Uruchom skrypt:
   ```
   python3 download_from_github.py
   ```
   Skrypt czyta pliki z `data/input/`, odpytuje GitHub GraphQL API (z opóźnieniem 0.2 s na użytkownika - dla dużej liczby loginów proces może trwać długo) i zapisuje wyniki cząstkowe jako
   `data/result/result_<numer>.csv`. Skrypt sam wznawia pracę od ostatniego przetworzonego pliku.
3. **Połącz** wszystkie pliki `result_*.csv` z `data/result/` w jeden plik `data_from_github.csv` i umieść go w `data/prepare_data/data_from_github.csv`.

### **Krok 2: Przygotowanie pliku CSV z danych z AIDEV**
1. Uruchom skrypt `collect_data.sql` z folderu `scripts/prepare_data`, a wynik zapytania zapisz jako
   `data/prepare_data/data_from_aidev.csv` (z nagłówkiem - kolumny muszą odpowiadać nazwom z zapytania:
   `login, followers, max_stars, max_forks, account_age, human_prs, total_commits, total_reviews, total_issues`).

### **Krok 3: Połączenie zbiorów i uzupełnienie braków danych**
1. Upewnij się, że posiadasz już pliki:
   - `data/prepare_data/data_from_aidev.csv`
   - `data/prepare_data/data_from_github.csv`
2. Uruchom skrypt uzupełniający brakujące dane (model RandomForest trenowany na części wspólnej obu
   zbiorów, przewiduje brakujące metryki GitHub dla reszty użytkowników):
   ```
   python3 random_forest.py
   ```
   Wynik zapisze się jako `data/prepare_data/final_combined_data.csv`.
### **Krok 4: Wyznaczenie optymalnej liczby klastrów**
1. Uruchom skrypt:
   ```
   python3 find_the_best_k.py
   ```
   Skrypt wczytuje `data/prepare_data/final_combined_data.csv` (surowe dane, przed PCA), stosuje
   `QuantileTransformer` + standaryzację i liczy Gap Statistic oraz Silhouette Score dla k = 2 - 10.
   Wyniki (wykresy) zapisują się w `results/gap_statistic_transformed.png` oraz
   `results/silhouette_score_transformed.png`. Na tej podstawie wybierz liczbę klastrów użytą w kroku 6.

### **Krok 5: Czyszczenie danych i redukcja PCA**
1. Uruchom skrypt:
   ```
   python3 filter_and_PCA.py
   ```
   Skrypt wczytuje `data/prepare_data/final_combined_data.csv`, usuwa outlierów metodą `IsolationForest`
   (contamination=0.01) i redukuje cechy do 2 głównych składowych (PCA). Wynik zapisuje jako
   `data/prepare_data/preprocessed_data.csv`, a wykresy wpływu zmiennych na PC1/PC2 zapisuje w
   `results/pca_pc1.png` i `results/pca_pc2.png`.

### **Krok 6: Algorytm k-means**
1. Uruchom skrypt:
   ```
   python3 k_means.py
   ```
   Skrypt wczytuje `data/prepare_data/preprocessed_data.csv` i klastruje użytkowników (domyślnie na 3
   grupy). Wynikiem jest plik `data/prepare_data/user_experience_levels.csv` zawierający mapowanie:
   `login -> experience` (Junior, Mid, Senior).

---

## Eksperymenty

### Eksperyment 1 - liczba pull requestów a poziom doświadczenia
1. Wykonaj skrypt `user_pull_request.sql` (folder `scripts/first_experiment`) i wynik zapisz **bez nagłówka** jako `data/first_experiment/pull_requests_sum.csv` (kolumny: login, liczba PR).
2. Uruchom skrypty w następującej kolejności:
   ```
   python3 scripts/first_experiment/run.py
   python3 scripts/first_experiment/plot.py
   ```
   Wyniki: `results/boxplot.png`, `results/summary_table.png`.

### Eksperyment 2 — wskaźnik akceptacji PR a poziom doświadczenia
Skrypty znajdują się w katalogu `scripts/second_experiment/`.
1. Uruchom `ratio_merge_request.sql` i wynik zapisz **bez nagłówka** jako
   `data/second_experiment/ratio_merge_requests_all.csv` (kolumny: login, total_mr, accepted_mr,
   rejected_mr, acceptance_rate).
2. Uruchom `run.py` - wykonuje test Kruskala-Wallisa i porównania parami (Mann-Whitney, korekta Bonferroniego), zapisuje `data/second_experiment/second_experiment_merged.csv`,
   `data/second_experiment/second_experiment_summary_stats.csv` oraz
   `results/second_experiment_boxplot.png`.
3. Uruchom `plot.py` — generuje `results/second_experiment_summary_table.png`.

### Eksperyment 3 — liczba komentarzy maintainerów a poziom doświadczenia
Skrypty znajdują się w katalogu `scripts/third_experiment/`.
1. Uruchom `data_to_third_experiment.sql` i wynik zapisz **z nagłówkiem** jako
   `data/third_experiment/data_to_third_experiment.csv` (kolumny: real_human_author,
   pull_request_id, comments_by_human_maintainers).
2. Uruchom `run.py` — testy statystyczne (Kruskal-Wallis + Mann-Whitney), zapisuje
   `data/third_experiment/third_experiment_summary_stats.csv` oraz
   `results/third_experiment_boxplot.png`, `results/third_experiment_summary_table.png`.
3. Uruchom `plot.py` (regeneruje tabelę podsumowującą z zapisanego CSV).