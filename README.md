# Projekt Badawczy

## 🇵🇱 Wersja polska

Plik zawiera opis odtworzenia wyników oraz kolejność uruchamiania skryptów wraz z opisem przetwarzanych danych. Analiza wyników znajduje się w pliku: [raport.pdf](raport.pdf)

### **Krok 0: Pobranie i podział danych wejściowych**
1. Pobierz dane z bazy **AIDEV** — Zenodo, wydanie v3, DOI `10.5281/zenodo.16919272`
   (https://zenodo.org/records/16919272).
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
1. Uruchom skrypt `collect_data.sql` z folderu `scripts/prepare_data`, a wynik zapytania
   zapisz jako `data/prepare_data/data_from_aidev.csv` (z nagłówkiem - kolumny muszą odpowiadać nazwom z zapytania:
   `login, followers, max_stars, max_forks, account_age, agent_activity_span_days, agent_diversity,
   agentic_repo_breadth`).
`agent_activity_span_days`/`agent_diversity`/`agentic_repo_breadth` liczone są z `all_pull_request`.

### **Krok 3: Połączenie zbiorów i uzupełnienie braków danych**
1. Upewnij się, że posiadasz już pliki:
   - `data/prepare_data/data_from_aidev.csv`
   - `data/prepare_data/data_from_github.csv`
2. Uruchom skrypt uzupełniający brakujące dane (model RandomForest trenowany na części wspólnej obu
   zbiorów, przewiduje brakujące metryki GitHub dla reszty użytkowników):
   ```
   python3 random_forest.py
   ```
   Skrypt najpierw robi split 80/20 na wspólnym zbiorze i liczy R² per wskaźnik (zapisuje do
   `data/prepare_data/random_forest_eval_r2.csv`), a dopiero
   potem doucza model na 100% wspólnych danych i tym modelem uzupełnia braki. Wynik główny zapisze się jako
   `data/prepare_data/final_combined_data.csv`.

### **Krok 4: Wyznaczenie optymalnej liczby klastrów**
1. Uruchom skrypt:
   ```
   python3 find_the_best_k.py
   ```
   Skrypt wczytuje `data/prepare_data/final_combined_data.csv` i stosuje: `log1p` → standaryzacja →
   `IsolationForest` (contamination=0.01). Gap Statistic i Silhouette Score dla
   $k \in \{2, 3, \dots, 10\}$ liczone są na pełnej, 12-wymiarowej, oczyszczonej reprezentacji, na której
   `k_means.py` faktycznie klastruje. Wyniki zapisują się w `results/gap_statistic_transformed.png`
   oraz `results/silhouette_score_transformed.png`. Na tej podstawie wybierz liczbę klastrów użytą w kroku 6.

### **Krok 5: Czyszczenie danych, właściwe dane do klastrowania i PCA do wizualizacji**
1. Uruchom skrypt:
   ```
   python3 filter_and_PCA.py
   ```
   Skrypt wczytuje `data/prepare_data/final_combined_data.csv`, stosuje `log1p` (normalizacja mocno
   prawoskośnych, zero-inflated cech) i standaryzację, usuwa outlierów metodą `IsolationForest`
   (contamination=0.01). Oczyszczoną, 12-wymiarową reprezentację zapisuje jako
   `data/prepare_data/preprocessed_data_12d.csv` — **to jest wejście do klastrowania** w kroku 6.
   Dodatkowo, obliczane jest PCA (2) do wizualizacji danych i zapisywane jako
   `data/prepare_data/preprocessed_data_pca2d.csv`, a wykresy wpływu zmiennych na PC1/PC2
   zapisuje w `results/pca_pc1.png` i `results/pca_pc2.png`.

### **Krok 6: Algorytm k-means**
1. Uruchom skrypt:
   ```
   python3 k_means.py
   ```
   Skrypt wczytuje `data/prepare_data/preprocessed_data_12d.csv` i klastruje użytkowników (domyślnie na 3 grupy) bezpośrednio na tych 12
   wymiarach. Wynikiem jest plik `data/prepare_data/user_experience_levels.csv` zawierający mapowanie:
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
   `run.py` wykonuje test Kruskala-Wallisa i porównania parami (Mann-Whitney dwustronny, korekta
   Bonferroniego, epsilon-squared i rank-biserial jako effect size).
   Wyniki: `results/boxplot.png`, `results/summary_table.png`.

### Eksperyment 2 - wskaźnik akceptacji PR a poziom doświadczenia
Skrypty znajdują się w katalogu `scripts/second_experiment/`.
1. Uruchom `ratio_merge_request.sql` — liczy acceptance rate z `all_pull_request` (Agentic-PRs),
   wykluczając otwarte PR-y z mianownika — i wynik zapisz **bez nagłówka** jako
   `data/second_experiment/ratio_merge_requests_all.csv` (kolumny: login, total_mr, accepted_mr,
   rejected_mr, acceptance_rate).
2. Uruchom `run.py` - wykonuje test Kruskala-Wallisa i porównania parami (Mann-Whitney **dwustronny**,
   korekta Bonferroniego, epsilon-squared i rank-biserial jako effect size), zapisuje
   `data/second_experiment/second_experiment_merged.csv`,
   `data/second_experiment/second_experiment_summary_stats.csv` oraz
   `results/second_experiment_boxplot.png`.
3. Uruchom `plot.py` - generuje `results/second_experiment_summary_table.png`.

### Eksperyment 3 - liczba komentarzy maintainerów a poziom doświadczenia
Skrypty znajdują się w katalogu `scripts/third_experiment/`.
1. Uruchom `data_to_third_experiment.sql` — ograniczone do AIDev-pop (tabela `pull_request`), liczy
   inline comments z `pr_review_comments_v2` i wynik zapisz **z nagłówkiem** jako
   `data/third_experiment/data_to_third_experiment.csv` (kolumny: real_human_author,
   pull_request_id, comments_by_human_maintainers).
2. Uruchom `run.py` - testy statystyczne (Kruskal-Wallis + Mann-Whitney dwustronny, epsilon-squared i
   rank-biserial jako effect size), zapisuje
   `data/third_experiment/third_experiment_summary_stats.csv` oraz
   `results/third_experiment_boxplot.png`, `results/third_experiment_summary_table.png`.
3. Uruchom `plot.py` (regeneruje tabelę podsumowującą z zapisanego CSV).

### Eksperyment 4 - acceptance rate Agentic-PR vs. baseline ludzki (RQ4)
Skrypty w `scripts/fourth_experiment/`. To porównanie dwóch niezależnych populacji.
1. Uruchom `human_pull_request_ratio.sql` i wynik zapisz **bez nagłówka** jako
   `data/fourth_experiment/human_pull_request_ratio.csv` (te same kolumny co w Eksperymencie 2:
   login, total_mr, accepted_mr, rejected_mr, acceptance_rate).
2. Uruchom `run.py` — wykorzystuje `data/second_experiment/ratio_merge_requests_all.csv` jako grupę Agent,
   liczy pojedynczy dwustronny test Manna-Whitneya (bez Kruskala-Wallisa, bo tylko 2 grupy) z
   rank-biserial jako effect size, zapisuje `data/fourth_experiment/fourth_experiment_merged.csv`,
   `data/fourth_experiment/fourth_experiment_summary_stats.csv` oraz
   `results/fourth_experiment_boxplot.png`.
3. Uruchom `plot.py` — generuje `results/fourth_experiment_summary_table.png`.
4. (Opcjonalnie) Uruchom `check_population_overlap.py` — sprawdza, ilu autorów `human_pull_request`
   pokrywa się z populacją agentową; wymaga `data/fourth_experiment/human_pull_request_authors.csv`
   (`SELECT DISTINCT user AS login FROM human_pull_request;`).

## Analizy wrażliwości
Skrypty w `scripts/sensitivity_analysis/`. Działają na plikach już wygenerowanych przez główny
pipeline (`data/prepare_data/`, `data/{first,second,third,fourth}_experiment/`), bez potrzeby dostępu
do surowego AIDev.

- **`preprocessing_stability_check.py`** — porównuje stabilność klastrowania dla
  `QuantileTransformer` i dla `log1p`.
- **`clustering_sensitivity_checks.py`** — cztery testy: alternatywne k (2/4/5), powtórzone
  inicjalizacje (5 seedów), zatrzymanie outlierów (bez Isolation Forest), wykluczenie 3 wskaźników
  z AIDev. Zapisuje `data/sensitivity_analysis/exclude_aidev_indicators_labels.csv`.
- **`rerun_rq1_rq2_excluding_aidev_indicators.py`** — RQ1/RQ2 pod klastrowaniem bez wskaźników
  agentowych (uruchom po `clustering_sensitivity_checks.py`).
- **`complete_case_rq_rerun.py`** — RQ1-RQ3 tylko na developerach z realnymi (nie imputowanymi)
  danymi z GraphQL. Zapisuje `data/sensitivity_analysis/complete_case_labels.csv`.
- **`bootstrap_effect_size_cis.py`** — 95% CI (bootstrap, 2000 powtórzeń) dla wszystkich effect sizes
  cytowanych w `ei-paper/4-results.tex`.

Wyniki tych skryptów są zacytowane w `ei-paper/5-threats.tex` i `ei-paper/6-conclusions.tex`.

## 🇬🇧 English version

This file describes how to reproduce the results, the order in which to run the scripts, and the data being processed.
The analysis of the results is in the file: [report.pdf](report.pdf)

### **Step 0: Downloading and splitting the input data**
1. Download the data from the **AIDEV** database — Zenodo, release v3, DOI `10.5281/zenodo.16919272`
   (https://zenodo.org/records/16919272).
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
1. Run the `collect_data.sql` script from the `scripts/prepare_data` folder (it first creates a
   `repository_owners` view derived from `all_repository.full_name`, since AIDev has no such table
   natively), and save the query result as `data/prepare_data/data_from_aidev.csv` (with a header - the
   columns must match the names from the query: `login, followers, max_stars, max_forks, account_age,
   agent_activity_span_days, agent_diversity, agentic_repo_breadth`).
   `agent_activity_span_days`/`agent_diversity`/`agentic_repo_breadth` are computed from
   `all_pull_request` (full scope, all 72,189 developers).

### **Step 3: Merging the datasets and filling in missing data**
1. Make sure you already have the files:
   - `data/prepare_data/data_from_aidev.csv`
   - `data/prepare_data/data_from_github.csv`
2. Run the script that fills in missing data (a RandomForest model trained on the intersection of both
   datasets predicts the missing GitHub metrics for the remaining users):
   ```
   python3 random_forest.py
   ```
   The script first does an 80/20 split on the overlapping users and reports R² per indicator (saved to
   `data/prepare_data/random_forest_eval_r2.csv` — these are the numbers to report in the methodology),
   then refits on 100% of the overlapping users and uses that model to impute the missing values. The main
   result is saved as `data/prepare_data/final_combined_data.csv`.

### **Step 4: Determining the optimal number of clusters**
1. Run the script:
   ```
   python3 find_the_best_k.py
   ```
   The script loads `data/prepare_data/final_combined_data.csv` and applies: `log1p` → standardization →
   `IsolationForest` (contamination=0.01) — no PCA. The Gap Statistic and Silhouette Score for
   $k \in \{2, 3, \dots, 10\}$ are computed on the full 12-D cleaned representation that `k_means.py`
   actually clusters on. The results (plots) are saved to `results/gap_statistic_transformed.png` and
   `results/silhouette_score_transformed.png`. Use these to choose the number of clusters used in Step 6.

### **Step 5: Data cleaning, clustering input, and PCA for visualization**
1. Run the script:
   ```
   python3 filter_and_PCA.py
   ```
   The script loads `data/prepare_data/final_combined_data.csv`, applies `log1p` (handles the strong
   right-skew / zero-inflation in the indicators) and standardization, and removes outliers using the
   `IsolationForest` method (contamination=0.01). The cleaned 12-D representation is saved as
   `data/prepare_data/preprocessed_data_12d.csv` -- **this is the clustering input** used in Step 6.
   Separately, purely for visualization/interpretation (not for clustering — PCA(2) retains only ~50% of
   variance), it computes PCA(2) on the same cleaned data and saves it as
   `data/prepare_data/preprocessed_data_pca2d.csv`, and saves the PC1/PC2 loadings plots to
   `results/pca_pc1.png` and `results/pca_pc2.png`.

### **Step 6: K-means algorithm**
1. Run the script:
   ```
   python3 k_means.py
   ```
   The script loads `data/prepare_data/preprocessed_data_12d.csv` (the full 12-D cleaned representation,
   **not** PCA) and clusters the users (into 3 groups by default) directly on those 12 dimensions. The
   result is the file `data/prepare_data/user_experience_levels.csv`, containing the mapping:
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
   `run.py` runs the Kruskal-Wallis test and pairwise comparisons (two-sided Mann-Whitney, Bonferroni
   correction, epsilon-squared and rank-biserial as effect size).
   Results: `results/boxplot.png`, `results/summary_table.png`.

### Experiment 2 - PR acceptance rate vs. experience level
Scripts are located in the `scripts/second_experiment/` directory.
1. Run `ratio_merge_request.sql` — computes acceptance rate from `all_pull_request` (Agentic-PRs),
   excluding open PRs from the denominator — and save the result **without a header** as
   `data/second_experiment/ratio_merge_requests_all.csv` (columns: login, total_mr, accepted_mr,
   rejected_mr, acceptance_rate).
2. Run `run.py` - it performs the Kruskal–Wallis test and pairwise comparisons (**two-sided** Mann–Whitney,
   Bonferroni correction, epsilon-squared and rank-biserial as effect size), and saves
   `data/second_experiment/second_experiment_merged.csv`,
   `data/second_experiment/second_experiment_summary_stats.csv`, and
   `results/second_experiment_boxplot.png`.
3. Run `plot.py` - generates `results/second_experiment_summary_table.png`.

### Experiment 3 - number of maintainer comments vs. experience level
Scripts are located in the `scripts/third_experiment/` directory.
1. Run `data_to_third_experiment.sql` — restricted to AIDev-pop (`pull_request` table), counts inline
   comments from `pr_review_comments_v2` (not `pr_review_comments`, which the AIDev documentation flags
   as incomplete) — and save the result **with a header** as
   `data/third_experiment/data_to_third_experiment.csv` (columns: real_human_author,
   pull_request_id, comments_by_human_maintainers).
2. Run `run.py` - statistical tests (Kruskal–Wallis + two-sided Mann–Whitney, epsilon-squared and
   rank-biserial as effect size), saves
   `data/third_experiment/third_experiment_summary_stats.csv` as well as
   `results/third_experiment_boxplot.png`, `results/third_experiment_summary_table.png`.
3. Run `plot.py` (regenerates the summary table from the saved CSV).

### Experiment 4 - Agentic-PR acceptance vs. a human-authored baseline (RQ4)
Scripts are located in the `scripts/fourth_experiment/` directory.
1. Run `human_pull_request_ratio.sql` and save the result **without a header** as
   `data/fourth_experiment/human_pull_request_ratio.csv` (same columns as Experiment 2:
   login, total_mr, accepted_mr, rejected_mr, acceptance_rate).
2. Run `run.py` - reuses `data/second_experiment/ratio_merge_requests_all.csv` as the Agent group, runs a
   single two-sided Mann-Whitney U test (no Kruskal-Wallis needed for 2 groups) with rank-biserial effect
   size, saves `data/fourth_experiment/fourth_experiment_merged.csv`,
   `data/fourth_experiment/fourth_experiment_summary_stats.csv`, and
   `results/fourth_experiment_boxplot.png`.
3. Run `plot.py` - generates `results/fourth_experiment_summary_table.png`.
4. (Optional) Run `check_population_overlap.py` — checks how many `human_pull_request` authors overlap
   with the agent-PR population; requires `data/fourth_experiment/human_pull_request_authors.csv`
   (`SELECT DISTINCT user AS login FROM human_pull_request;`).

## Sensitivity analyses
Scripts in `scripts/sensitivity_analysis/`. They run on files the main pipeline already produces
(`data/prepare_data/`, `data/{first,second,third,fourth}_experiment/`), without needing raw AIDev access.

- **`preprocessing_stability_check.py`** — compares clustering stability (Adjusted Rand Index between
  clustering the full population and the population without the RF-imputed developers) for
  `QuantileTransformer` and for `log1p`.
- **`clustering_sensitivity_checks.py`** — four checks: alternative k (2/4/5), repeated
  initializations (5 seeds), retained outliers (no Isolation Forest), and excluding the 3
  AIDev-derived indicators. Saves `data/sensitivity_analysis/exclude_aidev_indicators_labels.csv`.
- **`rerun_rq1_rq2_excluding_aidev_indicators.py`** — RQ1/RQ2 under the clustering without
  agent-usage indicators (run `clustering_sensitivity_checks.py` first).
- **`complete_case_rq_rerun.py`** — RQ1-RQ3 restricted to developers with real (non-imputed) GraphQL
  data. Saves `data/sensitivity_analysis/complete_case_labels.csv`.
- **`bootstrap_effect_size_cis.py`** — 95% bootstrap CIs (2,000 resamples) for every effect size
  quoted in `ei-paper/4-results.tex`.

These scripts' results are cited in `ei-paper/5-threats.tex` and `ei-paper/6-conclusions.tex`.
