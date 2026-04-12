# factorio-planner 🏭

> Production chain calculator for [Factorio](https://www.factorio.com/).

Given an item and a target production rate, **factorio-planner** resolves the full dependency tree and tells you exactly how many machines, furnaces and raw resources you need.

[![PyPI version](https://img.shields.io/pypi/v/factorio-planner.svg)](https://pypi.org/project/factorio-planner/)
[![Python](https://img.shields.io/pypi/pyversions/factorio-planner.svg)](https://pypi.org/project/factorio-planner/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/BernardRivera13/factorio-planner/actions/workflows/ci.yml/badge.svg)](https://github.com/BernardRivera13/factorio-planner/actions)

---

## ✨ Features

- **Full dependency resolution** — recursively resolves every ingredient down to raw ores/fluids
- **Machine counts** — calculates exact (fractional) machines needed per tier
- **Productivity & speed bonuses** — model module effects with a single parameter
- **CLI tool** — run `factorio-planner electronic-circuit --rate 10` directly in your terminal
- **JSON output** — machine-readable output for integration with other tools
- **Graph visualisation** — render the production chain as a directed graph (optional dep)
- **Extensible recipe DB** — load custom/modded recipes from JSON
- **Zero required dependencies** — core library needs nothing beyond the Python stdlib

---

## 📦 Installation

```bash
pip install factorio-planner
```

With graph visualisation support:

```bash
pip install "factorio-planner[graph]"
```

---

## 🚀 Quick start

### Python API

```python
from factorio_planner import Calculator

calc = Calculator()
plan = calc.compute("electronic-circuit", rate=10)
print(plan.summary())
```

Output:

```
Production plan: 10.00 electronic-circuit/s

Machines required:
  assembling-machine-1: 10.0
  stone-furnace: 22.4

Raw resources (per second):
  copper-ore: 15.00/s
  iron-ore: 10.00/s
```

### Full formatted plan with tree

```python
from factorio_planner import Calculator
from factorio_planner.formatter import format_plan

calc = Calculator()
plan = calc.compute("electronic-circuit", rate=10)
print(format_plan(plan))
```

```
────────────────────────────────────────────────────────────
  FACTORIO PRODUCTION PLAN
  Target: 10.00 × electronic-circuit / second
────────────────────────────────────────────────────────────

Production tree:

electronic-circuit  ×10.00/s  [×5.0 assembling-machine-1]
├── iron-plate  ×10.00/s  [×32.0 stone-furnace]
│   └── iron-ore  ×10.00/s  [RAW]
└── copper-cable  ×30.00/s  [×7.5 assembling-machine-1]
    └── copper-plate  ×15.00/s  [×48.0 stone-furnace]
        └── copper-ore  ×15.00/s  [RAW]
...
```

### With productivity modules

```python
# +40% productivity (research fully upgraded)
calc = Calculator(productivity_bonus=0.4)
plan = calc.compute("advanced-circuit", rate=5)
print(plan.summary())
```

### Visualise the production graph

```python
from factorio_planner import Calculator
from factorio_planner.graph import draw

calc = Calculator()
plan = calc.compute("utility-science-pack", rate=1)
fig = draw(plan)
fig.savefig("production_chain.png", dpi=150)
```

---

## 🖥️ CLI usage

```bash
# 10 electronic circuits per second
factorio-planner electronic-circuit --rate 10

# With productivity bonus
factorio-planner advanced-circuit --rate 5 --productivity 0.4

# JSON output (pipe-friendly)
factorio-planner iron-plate --rate 3 --json

# Skip tree, show only totals
factorio-planner utility-science-pack --rate 1 --no-tree
```

---

## 📓 Tutorial notebook

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BernardRivera13/factorio-planner/blob/main/docs/tutorial.ipynb)

The notebook walks through every feature step by step, from basic usage to full rocket-launch planning.

---

## 🔧 Custom / modded recipes

```python
import json
from factorio_planner import Calculator, RecipeDB
from factorio_planner.models import Recipe

# Option A: add one recipe programmatically
db = RecipeDB()
db.add(Recipe(
    name="my-mod-item",
    ingredients={"iron-plate": 3, "electronic-circuit": 1},
    products={"my-mod-item": 1},
    crafting_time=2.0,
    machine="assembling-machine-2",
))
calc = Calculator(db=db)

# Option B: load from JSON file
db2 = RecipeDB.from_json("my_mod_recipes.json")
calc2 = Calculator(db=db2)
```

---

## 🐳 Docker

```bash
# Run examples inside Docker
docker build -t factorio-planner .
docker run --rm factorio-planner factorio-planner electronic-circuit --rate 10
```

---

## 🧪 Running tests

```bash
pip install "factorio-planner[dev]"
pytest --cov=factorio_planner
```

---

## 📄 License

MIT — see [LICENSE](LICENSE).

> *factorio-planner is a fan project and is not affiliated with Wube Software.*
