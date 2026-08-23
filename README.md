# Projekt Badawczy

Plik zawiera opis odtworzenia wyników oraz kolejność uruchamiania skryptów wraz z opisem przetwarzanych danych.

### **Krok 0: Pobranie i podział danych wejściowych**
1. Pobierz dane z bazy **AIDEV** (https://huggingface.co/datasets/hao-li/AIDev/viewer/issue), a następnie wyciągnij listę wszystkich użytkowników za pomocą zapytania SQL:
    ```select login from all_user```
2. Wynik zapytania zapisz do pliku CSV.
3. Podziel plik na mniejsze części (po 100 autorów na plik) i umieść je w folderze `data/input/`.

### **Krok 1: Pobranie dodatkowych metryk z GitHub API**
Wszystkie niezbędne skrypty znajdziesz w folderze ```scripts/prepare_data ```
1. Uruchom skrypt:
    ```python3 download_from_github.py```
2. Wynik możemy znaleźć w pliku `data/result`. Należy połączyć mniejsze pliki w jeden plik `data_from_github.csv` i umieścić go w folderze `prepare_data`

### **Krok 2: Przygotowanie pliku csv z danych z **AIDEV**
1. Uruchom skrypt `collect_data.sql` z folderu `scripts/prepare_data` oraz wynik zapytania zapisz do pliku `data_from_aidev.csv` w folderze `data/prepare_data`.

### **Krok 3: Połączenie zbiorów i uzupełnienie braków danych**
1. Zakładając, że posiadasz już pliki:
    * `data_from_aidev.csv`
    * `data_from_github.csv`
2. Uruchom skrypt do uzupełnienia brakujących danych
    ```python3 random_forest.py```

### **Krok 4: Czyszczenie danych i redukcja PCA**
1. Uruchom skrypt:
    ```python3 filter_and_PCA.py```
    Skrypt usuwa outlierów oraz stosuje metodę PCA do wyodrębnienia najważniejszych cech.

### **Krok 5: Wyznaczenie optymalnej liczby klastrów**
1. Uruchom skrypt:
    ```python3 find_the_best_k.py```

### **Krok 6: Algorytm k - means**
1. Uruchom skrypt:
```python3 k_means.py```. Wynikiem jest plik `user_experience_levels.csv` zawierający mapowanie: login -> experience (Junior, Mid, Senior).

## Eksperymenty
### Eksperyment 1
1. Wykonaj skrypt `user_pull_request.sql` i wynik zapis w folderze `data/first_experiment/pull_requests_sum.csv`
2. Uruchom skrypty jest w następującej kolejności:
```
python3 scripts/first_experiment/run.py
python3 scripts/first_experiment/plot.py
```
### Eksperyment 2
Skrypty znajdują się w katalogu ```scripts/second_experiment/```
1. Uruchom `ratio_merge_request.sql` i wynik zapytania umieść w folderze `data/second_experiment`
2. Uruchom `run.py`
3. Uruchom `plot.py`

### Eksperyment 3
Skrypty znajdują się w katalogu ```scripts/third_experiment/```
1. Uruchom `data_to_third_experiment.sql` i wynik zapytania umieść w folderze `data/third_experiment`
2. Uruchom `run.py`
3. Uruchom `plot.py`

## Wyniki
Wszystkie wykresy, tabelki i wyniki skryptów znajdują się w folderze ```results```