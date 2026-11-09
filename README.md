# Assignment 8 Matplotlib

Donovan Mason · DSCI-D 211

This project compares physical measurements across three Iris species and explores the distribution of loan amounts, their relationship to applicant income, and how they vary across groups. All six visualizations use Matplotlib. Pandas reads, cleans, and summarizes the CSV data.

## Run the project

1. Install the dependencies with `python -m pip install -r requirements.txt`.
2. Run `python visualize.py` for the Iris charts.
3. Download the loan CSV from the Kaggle link in Canvas and run `python visualize.py --loan "path/to/loan.csv"` for all six charts. If the Kaggle download is a ZIP, extract the CSV first.
4. Open the PNG files and the generated `loan_analysis.md` in `charts/`.

The loan script recognizes common column names. If your file uses different ones, pass the actual headers. For example:

```sh
python visualize.py --loan "data/loans.csv" --amount-column "Loan Amount" --income-column "Annual Income" --group-column "Purpose"
```

Use `--output` to choose a different output directory and `--iris` to use a replacement Iris CSV with the same headers.

## Iris findings

| Chart | What it shows |
| --- | --- |
| [Petal scatter plot](charts/01_iris_petal_scatter.png) | Setosa forms a distinct cluster with short, narrow petals. Versicolor and virginica overlap near the edge of their clusters, but virginica tends to have larger petals. |
| [Sepal width box plot](charts/02_iris_sepal_boxplot.png) | Setosa has a higher median sepal width. The distributions overlap, so sepal width alone is less useful for distinguishing species than the two petal measurements together. |
| [Grouped trait means](charts/03_iris_trait_means.png) | Petal length has the largest spread in species means in centimeters. The averages of the sepal measurements are closer together. |

## Loan charts

| Chart | What it measures |
| --- | --- |
| Loan amount histogram | The distribution and median of positive, finite loan amounts. |
| Income and loan amount scatter plot | How loan amounts vary with positive, finite reported income. The income axis is logarithmic to spread out values when a few incomes are very large. |
| Group median bar chart | Median loan amounts for the most common groups, with the count beside each group name. |

## Class design

The classes keep data preparation and dataset-specific plots together. Shared functions handle formatting and PNG export.

| Class member | Purpose |
| --- | --- |
| `IrisAnalysis.__init__(csv_path)` | Loads the Iris file, checks for expected columns and species, converts measurements to numeric values, and drops incomplete rows. |
| `IrisAnalysis.data` | Cleaned Iris table. |
| `IrisAnalysis.traits` | Names and display order of the four measurement columns. |
| `IrisAnalysis.species` | Species names in a consistent display order across charts. |
| `IrisAnalysis.plot(output)` | Groups observations by species and saves three PNGs. |
| `LoanAnalysis.__init__(csv_path, amount, income, group)` | Loads the loan CSV, normalizes headers, resolves three distinct columns, and marks invalid numeric values as missing. The last three arguments are optional column overrides. |
| `LoanAnalysis.data` | Loan table with normalized headers and cleaned amount and income columns. |
| `LoanAnalysis.amount` | Header used for loan amounts. |
| `LoanAnalysis.income` | Header used for reported income. |
| `LoanAnalysis.group` | Header used for grouping, such as loan purpose or status. |
| `LoanAnalysis._column(requested, candidates)` | Finds an explicitly requested header or selects the first matching known header. Reports available columns if it cannot find one. |
| `LoanAnalysis.plot(output)` | Creates the three loan PNGs and writes a paragraph using the underlying statistics. |

The plotting methods expect an existing output directory. The command-line entry point creates it. The `chart`, `save`, `label`, and `compact` functions handle shared visual styling, export, readable labels, and compact tick values.

## Data and limitations

- The bundled Iris CSV contains 150 observations. It is a CSV export of the corrected Iris data distributed with scikit-learn, based on [Fisher's Iris dataset at UCI](https://archive.ics.uci.edu/dataset/53/iris). Running this project requires no scikit-learn installation.
- The assignment's Kaggle loan CSV is a separate input. Amounts and incomes retain their original units. Check the dataset documentation for the currency, scale, and reporting period.
- The loan figures can have different sample sizes because each uses the rows with the values it needs. Amount and income analyses use positive, finite values. Group comparisons require at least five observations per group and display at most the eight most frequent eligible groups. The scatter plot shows a fixed random sample of at most 5,000 pairs for readability. Pearson correlation uses all complete pairs on their original scales.
- These charts describe the supplied records. Group differences and correlation do not establish causation, and neither dataset necessarily represents a wider population.

## AI use

See [AI_CHAT_LOG.md](AI_CHAT_LOG.md) for the project-related exchange and a description of the AI-generated work.
