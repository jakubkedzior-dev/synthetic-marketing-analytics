# Marketing Analytics Dashboard — handoff i TODO

## 1. Przed wyjściem: zabezpiecz aktualną pracę

### Zapisz raport Power BI

W Power BI wybierz:

`File → Save As`

Zapisz plik w repozytorium jako:

`powerbi/marketing_analytics_dashboard.pbix`

Następnie wykonaj także:

`File → Export → PDF`

Jeżeli eksport do PDF jest dostępny, zapisz jako:

`powerbi/marketing_analytics_dashboard.pdf`

Zrób screenshot całej strony raportu i zapisz jako:

`screenshots/executive_overview.png`

### Wyślij zmiany na GitHuba

W terminalu VS Code, w głównym folderze projektu:

```powershell
git status
git add .
git commit -m "Add Power BI campaign performance dashboard"
git push
```

Po `git push` otwórz repozytorium w przeglądarce i sprawdź, czy widzisz:

- `powerbi/marketing_analytics_dashboard.pbix`
- `screenshots/executive_overview.png`
- `data/curated/campaign_performance.csv`
- foldery `python` i `sql`
- `README.md`

Jeżeli plik PBIX jest większy niż limit GitHuba, zachowaj go dodatkowo na OneDrive, Google Drive albo pendrivie. Kod, dane, README i screenshot nadal powinny znaleźć się w repozytorium.

## 2. Jak wznowić pracę na drugim komputerze

Zainstaluj:

- Git
- Python
- VS Code
- Power BI Desktop

W terminalu przejdź do folderu, w którym chcesz mieć projekt, i uruchom:

```powershell
git clone ADRES_TWOJEGO_REPOZYTORIUM
cd marketing-analytics-dashboard
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Sprawdź środowisko:

```powershell
python -c "import pandas, numpy, faker, duckdb, openpyxl, pyarrow; print('Environment works')"
```

Jeżeli chcesz odtworzyć dane:

```powershell
python .\python\generate_data.py
python .\python\prepare_data.py
```

Otwórz:

`powerbi/marketing_analytics_dashboard.pbix`

Raport pobiera tabelę `campaign_performance.csv` z publicznego adresu GitHub, więc lokalna ścieżka komputera nie powinna być potrzebna. Jeżeli Power BI zapyta o dostęp do źródła, wybierz `Anonymous`.

## 3. Najważniejsze poprawki w dashboardzie

### Obowiązkowe przed wysłaniem

- [ ] W środkowym wykresie zastąpić `ROAS Target Met` miarą `Selected ROAS Target`.
- [ ] Ustawić tytuł: `ROAS performance against target by campaign`.
- [ ] Ustawić `Overall Conversion Rate` jako Percentage, 1 decimal.
- [ ] Ustawić `Cost per Conversion` jako Currency, 2 decimals.
- [ ] Ustawić `Total Revenue` jako Currency.
- [ ] Poprawić miary `ROAS vs Target`, `Conversion vs Target` i `Target Status`, aby wiersz Total był pusty.
- [ ] Zmienić techniczne nazwy kolumn w tabeli przez `Rename for this visual`.
- [ ] Sprawdzić działanie filtrów `Channel` oraz `Target Segment`.
- [ ] Sprawdzić, czy po odświeżeniu wszystkie wizualizacje działają bez błędów.
- [ ] Zapisać finalny screenshot.

### Poprawione miary

```DAX
ROAS vs Target =
IF(
    ISINSCOPE(campaign_performance[campaign_name]),
    [Overall ROAS] - [Selected ROAS Target],
    BLANK()
)
```

```DAX
Conversion vs Target =
IF(
    ISINSCOPE(campaign_performance[campaign_name]),
    [Overall Conversion Rate] - [Selected Conversion Target],
    BLANK()
)
```

```DAX
Target Status =
IF(
    NOT ISINSCOPE(campaign_performance[campaign_name]),
    BLANK(),
    SWITCH(
        TRUE(),
        [ROAS vs Target] >= 0 && [Conversion vs Target] >= 0,
            "Both targets met",
        [ROAS vs Target] >= 0,
            "ROAS target only",
        [Conversion vs Target] >= 0,
            "Conversion target only",
        "Below both targets"
    )
)
```

## 4. Opcjonalne rozszerzenia — dopiero po ukończeniu MVP

- [ ] Zaimportować `customers.csv` jako `dim_customers`.
- [ ] Zaimportować `transactions.csv` jako `fact_transactions`.
- [ ] Utworzyć relację `dim_customers[customer_id]` 1:* `fact_transactions[customer_id]`.
- [ ] Dodać wymiar kampanii i model gwiazdy.
- [ ] Dodać drugą stronę `Customer & Loyalty`, jeżeli będą przygotowane dane na poziomie klienta.
- [ ] Dodać tooltip lub drill-through.

Nie są one wymagane przed interview. Obecna strona Executive Overview jest wystarczającym MVP.

## 5. Co powiedzieć o projekcie

> This is a compact marketing analytics project built entirely with synthetic data. Python was used for reproducible data generation and validation, DuckDB and SQL were used to prepare campaign-level analytical metrics, and Power BI was used as the semantic and presentation layer. The dashboard connects funnel engagement with commercial outcomes such as revenue, ROAS and target achievement.

O grainie i joinach:

> I defined the grain of every source before joining the datasets. Campaign events and transactions are separate fact-level datasets, so I aggregated both to campaign grain before joining them. This prevents row multiplication and overstated revenue.

O AI:

> AI supported ideation, debugging and documentation, while I reviewed the logic, implemented the workflow and validated the resulting metrics. All records are synthetic and reproducible.

## 6. Kryterium gotowości do wysłania

Projekt jest gotowy, jeżeli:

- dashboard otwiera się i odświeża;
- liczby mają poprawne formaty;
- filtry działają;
- total w tabeli nie pokazuje błędnego statusu;
- README wyjaśnia problem, narzędzia, metodologię i ograniczenia;
- repozytorium zawiera kod, SQL, dane syntetyczne oraz screenshot;
- potrafisz w 3 minuty wyjaśnić przepływ `synthetic sources → Python → DuckDB/SQL → Power BI`.

Nie dodawaj nowych funkcji przed spełnieniem tych punktów.
