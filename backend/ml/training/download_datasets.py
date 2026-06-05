"""
Download and prepare fake news datasets for training.

Datasets:
- ISOT Fake News Dataset (via bundled CSV or Kaggle)
- LIAR Dataset (from public TSV files)
"""
import os
import json
import csv
import urllib.request
import zipfile
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"


def download_file(url: str, dest: Path):
    """Download a file from URL to destination."""
    if dest.exists():
        print(f"  Already exists: {dest}")
        return
    print(f"  Downloading {url} -> {dest}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, str(dest))


def prepare_liar_dataset():
    """
    Download and prepare the LIAR dataset.
    The LIAR dataset has 6 labels: pants-fire, false, barely-true, half-true, mostly-true, true
    We binarize: pants-fire/false/barely-true -> fake, half-true/mostly-true/true -> real
    """
    print("\n=== Preparing LIAR Dataset ===")
    liar_dir = DATA_DIR / "liar"
    liar_dir.mkdir(parents=True, exist_ok=True)

    base_url = "https://www.cs.ucsb.edu/~william/data"
    files = {
        "train": "train.tsv",
        "val": "valid.tsv",
        "test": "test.tsv",
    }

    fake_labels = {"pants-fire", "false", "barely-true"}
    real_labels = {"half-true", "mostly-true", "true"}

    all_data = []

    for split, filename in files.items():
        filepath = liar_dir / filename
        # Try to download; if it fails, generate synthetic data
        try:
            download_file(f"{base_url}/{filename}", filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter="\t")
                for row in reader:
                    if len(row) >= 3:
                        label_raw = row[1].strip().lower()
                        statement = row[2].strip()
                        if label_raw in fake_labels:
                            all_data.append({"text": statement, "label": 1, "source": "liar"})
                        elif label_raw in real_labels:
                            all_data.append({"text": statement, "label": 0, "source": "liar"})
        except Exception as e:
            print(f"  Could not download {filename}: {e}")
            print("  Generating synthetic LIAR-style data...")

    if not all_data:
        all_data = _generate_synthetic_data()

    print(f"  Total LIAR samples: {len(all_data)}")
    return all_data


def prepare_isot_dataset():
    """
    Prepare ISOT-style dataset.
    Since ISOT requires Kaggle auth, we generate realistic synthetic data
    matching the ISOT format (title + text, binary label).
    """
    print("\n=== Preparing ISOT-style Dataset ===")
    isot_dir = DATA_DIR / "isot"
    isot_dir.mkdir(parents=True, exist_ok=True)

    true_path = isot_dir / "True.csv"
    fake_path = isot_dir / "Fake.csv"

    all_data = []

    # Try loading existing CSVs first
    if true_path.exists() and fake_path.exists():
        print("  Loading existing ISOT CSVs...")
        try:
            true_df = pd.read_csv(true_path)
            for _, row in true_df.iterrows():
                text = f"{row.get('title', '')} {row.get('text', '')}"
                all_data.append({"text": text.strip(), "label": 0, "source": "isot"})

            fake_df = pd.read_csv(fake_path)
            for _, row in fake_df.iterrows():
                text = f"{row.get('title', '')} {row.get('text', '')}"
                all_data.append({"text": text.strip(), "label": 1, "source": "isot"})
        except Exception as e:
            print(f"  Error reading CSVs: {e}")
            all_data = []

    if not all_data:
        print("  ISOT CSVs not found. Generating synthetic training data...")
        all_data = _generate_synthetic_data()

    print(f"  Total ISOT-style samples: {len(all_data)}")
    return all_data


def _generate_synthetic_data():
    """Generate synthetic fake news dataset for training when real datasets unavailable."""
    data = []

    # Real news patterns
    real_templates = [
        "The Federal Reserve announced a quarter-point interest rate increase on Wednesday, citing continued economic growth and low unemployment figures.",
        "Researchers at MIT published findings in Nature showing a new method for carbon capture that could reduce industrial emissions by 30 percent.",
        "The Senate passed the infrastructure bill with bipartisan support, allocating $550 billion for roads, bridges, and broadband internet.",
        "According to the World Health Organization, global vaccination rates for COVID-19 have reached 65 percent across developed nations.",
        "NASA's Perseverance rover collected its tenth rock sample on Mars, which scientists say could contain signs of ancient microbial life.",
        "The unemployment rate fell to 3.5 percent in the latest Bureau of Labor Statistics report, matching pre-pandemic levels.",
        "A peer-reviewed study in The Lancet confirmed that the new antiviral treatment reduces hospitalization risk by 89 percent in clinical trials.",
        "The Supreme Court ruled 6-3 in favor of the plaintiff, establishing new precedent for digital privacy protections under the Fourth Amendment.",
        "International trade negotiations concluded with a new framework agreement between the EU and ASEAN nations covering tariff reductions.",
        "Climate scientists reported that Arctic sea ice reached its second-lowest extent on record this September, according to satellite data.",
        "The central bank maintained its benchmark interest rate at 5.25 percent, signaling a pause in the tightening cycle.",
        "A team of astronomers using the James Webb Space Telescope identified water vapor in the atmosphere of a potentially habitable exoplanet.",
        "The Department of Education released new guidelines for standardized testing in public schools, effective next academic year.",
        "Economists project GDP growth of 2.1 percent for the current fiscal quarter based on consumer spending and manufacturing data.",
        "The FDA approved a new gene therapy treatment for sickle cell disease after Phase III trials showed significant clinical improvement.",
        "Local authorities reported a 12 percent decrease in property crime rates compared to the same quarter last year.",
        "The international scientific community published a consensus statement on biodiversity loss, signed by representatives from 45 countries.",
        "Municipal bonds in the transportation sector saw increased demand following the announcement of new public transit investments.",
        "Agricultural exports increased by 8 percent year over year according to the latest USDA trade report.",
        "The National Weather Service issued updated seasonal forecasts predicting above-average temperatures for the eastern United States.",
    ]

    fake_templates = [
        "BREAKING: Secret government documents LEAKED reveal they've been hiding the cure for cancer for decades! Big Pharma doesn't want you to know!",
        "SHOCKING: Celebrity found dead, but mainstream media is covering it up! Share before they delete this!",
        "Scientists CONFIRM that 5G towers are causing mysterious illness in thousands of people - the evidence is UNDENIABLE!",
        "You WON'T BELIEVE what this politician was caught doing! The deep state tried to bury this story!",
        "EXPOSED: The election was STOLEN using secret algorithms in voting machines! Millions of fake ballots found!",
        "ALERT: New world order plan REVEALED - global elites are planning to microchip the entire population by 2025!",
        "MIRACLE cure discovered in remote village - doctors HATE this one simple trick that cures diabetes overnight!",
        "URGENT: Banks are about to COLLAPSE! Move your money NOW before it's too late! The government is lying to you!",
        "PROOF that the moon landing was FAKED - NASA whistleblower releases never-before-seen footage!",
        "BOMBSHELL: Vaccines contain SECRET tracking nanobots! Internal Pfizer documents EXPOSED by anonymous insider!",
        "THEY don't want you to see this! The REAL reason gas prices are high - it's all a deliberate CONSPIRACY!",
        "DISGUSTING: Politician caught in MASSIVE corruption scandal, but the biased media won't report it!",
        "WARNING: Eating this common food is KILLING you slowly! Doctors have been LYING about nutrition for years!",
        "UNBELIEVABLE: Child actor reveals Hollywood's DARKEST secret that will shake you to your core!",
        "BREAKING EXCLUSIVE: Alien technology found in Antarctica - world governments form SECRET alliance to hide truth!",
        "HIDDEN CAMERA footage shows what REALLY happens inside fast food restaurants - you'll never eat there again!",
        "BANNED video reveals the TRUTH about what chemtrails are really doing to our water supply!",
        "EXPLOSIVE report: Top scientist ADMITS climate change is a HOAX designed to control the population!",
        "SHARE BEFORE DELETED: Leaked audio of world leaders discussing population reduction plan!",
        "STUNNING: Famous billionaire secretly funding underground cities for the elite while normal people suffer!",
    ]

    import random
    random.seed(42)

    # Generate variations
    for template in real_templates:
        for i in range(50):
            # Create variations by slight modifications
            text = template
            if i % 3 == 0:
                text = "According to officials, " + text[0].lower() + text[1:]
            elif i % 3 == 1:
                text = "Reports indicate that " + text[0].lower() + text[1:]
            else:
                text = text + " Officials confirmed the report on Tuesday."
            data.append({"text": text, "label": 0, "source": "synthetic"})

    for template in fake_templates:
        for i in range(50):
            text = template
            if i % 3 == 0:
                text = "JUST IN: " + text
            elif i % 3 == 1:
                text = text + " WAKE UP PEOPLE!"
            else:
                text = text + " Share this before it gets censored!"
            data.append({"text": text, "label": 1, "source": "synthetic"})

    random.shuffle(data)
    return data


def prepare_all_datasets():
    """Download and merge all datasets, split into train/val/test."""
    print("Preparing datasets...")

    liar_data = prepare_liar_dataset()
    isot_data = prepare_isot_dataset()

    all_data = liar_data + isot_data

    import random
    random.seed(42)
    random.shuffle(all_data)

    n = len(all_data)
    train_end = int(0.8 * n)
    val_end = int(0.9 * n)

    splits = {
        "train": all_data[:train_end],
        "val": all_data[train_end:val_end],
        "test": all_data[val_end:],
    }

    output_dir = DATA_DIR / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    for split_name, split_data in splits.items():
        path = output_dir / f"{split_name}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(split_data, f, indent=2)
        label_counts = {}
        for item in split_data:
            label_counts[item["label"]] = label_counts.get(item["label"], 0) + 1
        print(f"  {split_name}: {len(split_data)} samples - {label_counts}")

    print(f"\nTotal: {n} samples")
    print(f"Saved to {output_dir}")
    return splits


if __name__ == "__main__":
    prepare_all_datasets()
