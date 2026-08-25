# Projekt Badawczy

## 🇵🇱 Wersja polska

Plik zawiera opis odtworzenia wyników oraz kolejność uruchamiania skryptów wraz z opisem przetwarzanych danych. Analiza wyników znajduje się w pliku: [raport.pdf](raport.pdf)

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

### Eksperyment 2 - wskaźnik akceptacji PR a poziom doświadczenia
Skrypty znajdują się w katalogu `scripts/second_experiment/`.
1. Uruchom `ratio_merge_request.sql` i wynik zapisz **bez nagłówka** jako
   `data/second_experiment/ratio_merge_requests_all.csv` (kolumny: login, total_mr, accepted_mr,
   rejected_mr, acceptance_rate).
2. Uruchom `run.py` - wykonuje test Kruskala-Wallisa i porównania parami (Mann-Whitney, korekta Bonferroniego), zapisuje `data/second_experiment/second_experiment_merged.csv`,
   `data/second_experiment/second_experiment_summary_stats.csv` oraz
   `results/second_experiment_boxplot.png`.
3. Uruchom `plot.py` - generuje `results/second_experiment_summary_table.png`.

### Eksperyment 3 - liczba komentarzy maintainerów a poziom doświadczenia
Skrypty znajdują się w katalogu `scripts/third_experiment/`.
1. Uruchom `data_to_third_experiment.sql` i wynik zapisz **z nagłówkiem** jako
   `data/third_experiment/data_to_third_experiment.csv` (kolumny: real_human_author,
   pull_request_id, comments_by_human_maintainers).
2. Uruchom `run.py` - testy statystyczne (Kruskal-Wallis + Mann-Whitney), zapisuje
   `data/third_experiment/third_experiment_summary_stats.csv` oraz
   `results/third_experiment_boxplot.png`, `results/third_experiment_summary_table.png`.
3. Uruchom `plot.py` (regeneruje tabelę podsumowującą z zapisanego CSV).


## 🇬🇧 English version

This file describes how to reproduce the results, the order in which to run the scripts, and the data being processed.
The analysis of the results is in the file: [report.pdf](report.pdf)
### **Step 0: Downloading and splitting the input data**
1. Download the data from the **AIDEV** database (https://huggingface.co/datasets/hao-li/AIDev/viewer/issue).
2. Extract the list of all users using the SQL query:
   ```sql
   SELECT login FROM all_user
   ```
3. Save the query result to a CSV file **without a header row** (the scripts in Step 1 read the files assuming there is no header).
4. Split the file into smaller parts (100 logins per file), name them with consecutive numbers (`1.csv`, `2.csv`, ...), and place them in the `data/input/` folder.

### **Step 1: Downloading additional metrics from the GitHub API**
All the necessary scripts can be found in the `scripts/prepare_data` folder.

1. In `download_from_github.py`, fill in `GITHUB_TOKEN`.
2. Run the script:
   ```
   python3 download_from_github.py
   ```
   The script reads the files from `data/input/`, queries the GitHub GraphQL API (with a 0.2 s delay per
   user - for a large number of logins the process may take a long time), and saves partial results as
   `data/result/result_<number>.csv`. The script automatically resumes from the last processed file.
3. **Merge** all `result_*.csv` files from `data/result/` into a single file `data_from_github.csv` and place it in `data/prepare_data/data_from_github.csv`.

### **Step 2: Preparing the CSV file from the AIDEV data**
1. Run the `collect_data.sql` script from the `scripts/prepare_data` folder, and save the query result as `data/prepare_data/data_from_aidev.csv` (with a header - the columns must match the names from the query: `login, followers, max_stars, max_forks, account_age, human_prs, total_commits, total_reviews, total_issues`).

### **Step 3: Merging the datasets and filling in missing data**
1. Make sure you already have the files:
   - `data/prepare_data/data_from_aidev.csv`
   - `data/prepare_data/data_from_github.csv`
2. Run the script that fills in missing data (a RandomForest model trained on the intersection of both
   datasets predicts the missing GitHub metrics for the remaining users):
   ```
   python3 random_forest.py
   ```
   The result will be saved as `data/prepare_data/final_combined_data.csv`.

### **Step 4: Determining the optimal number of clusters**
1. Run the script:
   ```
   python3 find_the_best_k.py
   ```
   The script loads `data/prepare_data/final_combined_data.csv` (raw data, before PCA), applies a
   `QuantileTransformer` + standardization, and computes the Gap Statistic and Silhouette Score for k = 2–10.
   The results (plots) are saved to `results/gap_statistic_transformed.png` and
   `results/silhouette_score_transformed.png`. Use these to choose the number of clusters used in Step 6.

### **Step 5: Data cleaning and PCA reduction**
1. Run the script:
   ```
   python3 filter_and_PCA.py
   ```
   The script loads `data/prepare_data/final_combined_data.csv`, removes outliers using the `IsolationForest`
   method (contamination=0.01), and reduces the features to 2 principal components (PCA). The result is saved as
   `data/prepare_data/preprocessed_data.csv`, and plots of variable influence on PC1/PC2 are saved to
   `results/pca_pc1.png` and `results/pca_pc2.png`.

### **Step 6: K-means algorithm**
1. Run the script:
   ```
   python3 k_means.py
   ```
   The script loads `data/prepare_data/preprocessed_data.csv` and clusters the users (into 3 groups by
   default). The result is the file `data/prepare_data/user_experience_levels.csv`, containing the mapping:
   `login -> experience` (Junior, Mid, Senior).

---

## Experiments

### Experiment 1 - number of pull requests vs. experience level
1. Run the `user_pull_request.sql` script (folder `scripts/first_experiment`) and save the result **without a header** as `data/first_experiment/pull_requests_sum.csv` (columns: login, number of PRs).
2. Run the scripts in the following order:
   ```
   python3 scripts/first_experiment/run.py
   python3 scripts/first_experiment/plot.py
   ```
   Results: `results/boxplot.png`, `results/summary_table.png`.

### Experiment 2 - PR acceptance rate vs. experience level
Scripts are located in the `scripts/second_experiment/` directory.
1. Run `ratio_merge_request.sql` and save the result **without a header** as
   `data/second_experiment/ratio_merge_requests_all.csv` (columns: login, total_mr, accepted_mr,
   rejected_mr, acceptance_rate).
2. Run `run.py` - it performs the Kruskal–Wallis test and pairwise comparisons (Mann–Whitney, Bonferroni
   correction), and saves `data/second_experiment/second_experiment_merged.csv`,
   `data/second_experiment/second_experiment_summary_stats.csv`, and
   `results/second_experiment_boxplot.png`.
3. Run `plot.py` - generates `results/second_experiment_summary_table.png`.

### Experiment 3 - number of maintainer comments vs. experience level
Scripts are located in the `scripts/third_experiment/` directory.
1. Run `data_to_third_experiment.sql` and save the result **with a header** as
   `data/third_experiment/data_to_third_experiment.csv` (columns: real_human_author,
   pull_request_id, comments_by_human_maintainers).
2. Run `run.py` - statistical tests (Kruskal–Wallis + Mann–Whitney), saves
   `data/third_experiment/third_experiment_summary_stats.csv` as well as
   `results/third_experiment_boxplot.png`, `results/third_experiment_summary_table.png`.
3. Run `plot.py` (regenerates the summary table from the saved CSV).
