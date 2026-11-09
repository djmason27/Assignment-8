"""Create Iris and loan charts with Matplotlib."""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd


COLORS = ("#006C75", "#B74F23", "#594596")
ROOT = Path(__file__).resolve().parent


class IrisAnalysis:
    """Compare four physical measurements across the three Iris species."""

    def __init__(self, csv_path):
        self.data = pd.read_csv(csv_path)
        self.traits = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
        self.species = ["setosa", "versicolor", "virginica"]
        if not set(self.traits + ["species"]).issubset(self.data.columns):
            raise ValueError("The Iris CSV must contain all four traits and species.")
        self.data[self.traits] = self.data[self.traits].apply(pd.to_numeric, errors="raise")
        self.data = self.data.dropna(subset=self.traits + ["species"])
        if set(self.data["species"]) != set(self.species):
            raise ValueError("The Iris CSV must contain all three expected species.")

    def plot(self, output):
        """Save a scatter plot, a box plot, and a grouped bar chart."""
        groups = [self.data[self.data["species"] == name] for name in self.species]
        labels = [name.title() for name in self.species]

        fig, ax = chart("Petal size separates the iris species")
        for group, name, color, marker in zip(groups, labels, COLORS, ("o", "s", "^")):
            ax.scatter(group["petal_length"], group["petal_width"], label=name,
                       color=color, marker=marker, alpha=0.75, edgecolors="white",
                       linewidths=0.45, s=48)
        ax.set(xlabel="Petal length (cm)", ylabel="Petal width (cm)")
        ax.legend(frameon=False)
        save(fig, output, "01_iris_petal_scatter.png")

        fig, ax = chart("Sepal widths overlap across species")
        boxes = ax.boxplot([group["sepal_width"] for group in groups],
                           patch_artist=True, medianprops={"color": "white", "linewidth": 2})
        ax.set_xticks(range(1, 4), labels)
        for box, color in zip(boxes["boxes"], COLORS):
            box.set_facecolor(color)
        ax.set(xlabel="Species", ylabel="Sepal width (cm)")
        save(fig, output, "02_iris_sepal_boxplot.png")

        fig, ax = chart("Average petal size varies more across species")
        positions = range(len(self.traits))
        for index, (group, name, color) in enumerate(zip(groups, labels, COLORS)):
            ax.bar([x + (index - 1) * 0.24 for x in positions], group[self.traits].mean(),
                   width=0.24, label=name, color=color)
        ax.set_xticks(positions, [trait.replace("_", " ").title() for trait in self.traits])
        ax.set(ylabel="Mean measurement (cm)", ylim=(0, self.data[self.traits].max().max() * 1.15))
        ax.legend(frameon=False, ncols=3, loc="upper left")
        save(fig, output, "03_iris_trait_means.png")


class LoanAnalysis:
    """Explore loan amounts, their relationship to income, and group differences."""

    def __init__(self, csv_path, amount=None, income=None, group=None):
        self.data = pd.read_csv(csv_path)
        self.data.columns = self.data.columns.str.strip().str.lower().str.replace(r"[\s-]+", "_", regex=True)
        if not self.data.columns.is_unique:
            raise ValueError("The loan CSV contains duplicate column names.")
        self.amount = self._column(amount, ("loan_amount", "loanamnt", "loan_amt",
                                             "loanamount", "loan_amnt", "funded_amnt"))
        self.income = self._column(income, ("person_income", "annual_income", "annual_inc",
                                             "applicantincome", "applicant_income", "income_annum", "income"))
        self.group = self._column(group, ("loan_intent", "purpose", "loan_purpose", "loan_status",
                                         "grade", "loan_grade", "education", "term"))
        if len({self.amount, self.income, self.group}) != 3:
            raise ValueError("Amount, income, and group must use distinct columns.")
        for column in (self.amount, self.income):
            self.data[column] = pd.to_numeric(self.data[column], errors="coerce")
            self.data.loc[~self.data[column].between(0, float("inf"), inclusive="neither"), column] = float("nan")

    def _column(self, requested, candidates):
        """Resolve an override or the first recognized CSV header."""
        options = (requested.strip().lower().replace(" ", "_").replace("-", "_"),) if requested else candidates
        for column in options:
            if column in self.data.columns:
                return column
        raise ValueError(f"Missing column. Expected one of {', '.join(options)}. "
                         f"Available columns: {', '.join(self.data.columns)}.")

    def plot(self, output):
        """Save three charts and a paragraph computed from the plotted records."""
        amounts = self.data[self.amount].dropna()
        pairs = self.data[[self.income, self.amount]].dropna()
        groups = self.data[[self.group, self.amount]].dropna()
        groups = groups.assign(**{self.group: groups[self.group].astype(str).str.strip()})
        groups = groups[groups[self.group] != ""]
        counts = groups[self.group].value_counts()
        selected = counts[counts >= 5].head(8).index
        if amounts.empty or len(pairs) < 2 or len(selected) < 2:
            raise ValueError("Need valid loan amounts, two income–amount pairs, and two groups with at least five records each.")
        summary = groups[groups[self.group].isin(selected)].groupby(self.group)[self.amount].agg(
            median="median", count="size").sort_values("median")

        fig, ax = chart("How loan amounts are distributed")
        ax.hist(amounts, bins=24, color=COLORS[0], edgecolor="white")
        ax.axvline(amounts.median(), color=COLORS[1], linewidth=2,
                   label=f"Median {amounts.median():,.0f}")
        ax.set(xlabel=label(self.amount), ylabel="Number of records")
        ax.xaxis.set_major_formatter(FuncFormatter(compact))
        ax.legend(frameon=False)
        save(fig, output, "04_loan_amount_distribution.png")

        fig, ax = chart("Loan amount across reported incomes")
        shown = pairs.sample(5000, random_state=8) if len(pairs) > 5000 else pairs
        ax.scatter(shown[self.income], shown[self.amount], s=15, alpha=0.25,
                   color=COLORS[0], linewidths=0, label=f"{len(shown):,} records shown")
        ax.set(xlabel=f"{label(self.income)} (log scale)", ylabel=label(self.amount), xscale="log")
        ax.yaxis.set_major_formatter(FuncFormatter(compact))
        ax.legend(frameon=False)
        save(fig, output, "05_loan_income_scatter.png")

        fig, ax = chart(f"Median loan amount by {label(self.group).lower()}")
        display = [f"{name}  (n={count:,})" for name, count in summary["count"].items()]
        bars = ax.barh(display, summary["median"], color=COLORS[2])
        ax.bar_label(bars, labels=[f"{value:,.0f}" for value in summary["median"]], padding=4)
        ax.set(xlabel=f"Median {label(self.amount).lower()}",
               xlim=(0, summary["median"].max() * 1.27))
        ax.grid(False, axis="y")
        ax.grid(True, axis="x", color="#E1E6EB", linewidth=0.8)
        ax.xaxis.set_major_formatter(FuncFormatter(compact))
        save(fig, output, "06_loan_group_medians.png")

        low, high = summary.iloc[0], summary.iloc[-1]
        correlation = pairs[self.income].corr(pairs[self.amount])
        association = (f"The Pearson correlation across all {len(pairs):,} complete pairs was "
                       f"{correlation:.2f} (calculated on the original scale)."
                       if pd.notna(correlation) else
                       "Pearson correlation was undefined because a variable had no variation.")
        (output / "loan_analysis.md").write_text(
            "# Loan Data Analysis\n\n"
            f"The histogram shows a median loan amount of {amounts.median():,.0f} across "
            f"{len(amounts):,} records, with the middle half ranging from "
            f"{amounts.quantile(.25):,.0f} to {amounts.quantile(.75):,.0f}. "
            f"The scatter plot compares {label(self.income).lower()} with loan amount. "
            f"{association} The group chart shows that, among the groups displayed, "
            f"{summary.index[-1]} had a median of {high['median']:,.0f} "
            f"(n={int(high['count']):,}), while {summary.index[0]} had a median of "
            f"{low['median']:,.0f} (n={int(low['count']):,}). These differences describe "
            "the records in this CSV. Other borrower characteristics may explain part of "
            "the variation, so the charts cannot establish what causes loan amounts to differ.\n",
            encoding="utf-8",
        )


def label(column):
    """Render common abbreviated headers as readable axis labels."""
    if column in {"loanamnt", "loan_amt", "loanamount", "loan_amnt", "loan_amount"}:
        return "Loan amount"
    if column in {"annual_inc", "annual_income", "income_annum"}:
        return "Annual income"
    if column == "applicantincome":
        return "Applicant income"
    return column.replace("_", " ").capitalize()


def compact(value, _):
    """Format large axis ticks without implying an unverified currency."""
    return f"{value / 1000:g}k" if abs(value) >= 1000 else f"{value:g}"


def chart(title):
    """Create a figure with a common title, grid, and type scale."""
    fig, ax = plt.subplots(figsize=(9, 5.4), layout="constrained")
    ax.set_title(title, loc="left", fontweight="bold", fontsize=17, pad=14)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#E1E6EB", linewidth=0.8)
    return fig, ax


def save(fig, output, filename):
    """Write a PNG and release the figure's memory."""
    fig.savefig(output / filename, dpi=160, facecolor="white")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loan", type=Path, help="CSV downloaded from the assignment's Kaggle link")
    parser.add_argument("--iris", type=Path, default=ROOT / "data" / "iris.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "charts")
    parser.add_argument("--amount-column")
    parser.add_argument("--income-column")
    parser.add_argument("--group-column")
    args = parser.parse_args()
    try:
        args.output.mkdir(parents=True, exist_ok=True)
        IrisAnalysis(args.iris).plot(args.output)
        if args.loan:
            LoanAnalysis(args.loan, args.amount_column, args.income_column,
                         args.group_column).plot(args.output)
        else:
            print("Iris charts created. Pass --loan PATH to create the loan charts and analysis.")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Could not complete the charts: {error}\n")


if __name__ == "__main__":
    main()
