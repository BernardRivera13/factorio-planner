"""Tests for the Calculator engine."""
import math
import pytest
from factorio_planner import Calculator, RecipeDB
from factorio_planner.models import ProductionPlan


@pytest.fixture
def calc():
    return Calculator()


class TestBasicCompute:
    def test_raw_resource_has_no_children(self, calc):
        plan = calc.compute("iron-ore", rate=1.0)
        assert plan.root.is_raw()
        assert plan.root.children == []

    def test_iron_plate_requires_furnaces(self, calc):
        plan = calc.compute("iron-plate", rate=1.0)
        assert not plan.root.is_raw()
        assert plan.root.machines_needed > 0
        assert "stone-furnace" in plan.machine_totals

    def test_iron_plate_raw_resource_is_iron_ore(self, calc):
        plan = calc.compute("iron-plate", rate=1.0)
        assert "iron-ore" in plan.raw_resources
        assert plan.raw_resources["iron-ore"] == pytest.approx(1.0)

    def test_electronic_circuit_raw_resources(self, calc):
        plan = calc.compute("electronic-circuit", rate=1.0)
        assert "iron-ore" in plan.raw_resources
        assert "copper-ore" in plan.raw_resources

    def test_rate_scales_linearly(self, calc):
        plan1 = calc.compute("iron-plate", rate=1.0)
        plan2 = calc.compute("iron-plate", rate=5.0)
        assert plan2.root.machines_needed == pytest.approx(plan1.root.machines_needed * 5, rel=1e-4)
        assert plan2.raw_resources["iron-ore"] == pytest.approx(5.0)


class TestMachineCounts:
    def test_iron_plate_machine_count(self, calc):
        # iron-plate: time=3.2, yield=1, stone-furnace speed=1.0
        # machines = (1/1) * 3.2 / 1.0 = 3.2
        plan = calc.compute("iron-plate", rate=1.0)
        assert plan.root.machines_needed == pytest.approx(3.2)

    def test_copper_cable_yield_two(self, calc):
        # copper-cable yields 2 per craft, time=0.5, machine speed=0.5
        # rate=1, yield=2 => crafts/s=0.5, time=0.5, speed=0.5 => machines=0.5*0.5/0.5=0.5
        plan = calc.compute("copper-cable", rate=1.0)
        assert plan.root.machines_needed == pytest.approx(0.5)

    def test_productivity_reduces_machines(self):
        calc_no_prod = Calculator(productivity_bonus=0.0)
        calc_prod = Calculator(productivity_bonus=0.4)
        plan_no = calc_no_prod.compute("iron-plate", rate=1.0)
        plan_pr = calc_prod.compute("iron-plate", rate=1.0)
        assert plan_pr.root.machines_needed < plan_no.root.machines_needed

    def test_speed_bonus_reduces_machines(self):
        calc_base = Calculator(speed_bonus=0.0)
        calc_fast = Calculator(speed_bonus=1.0)
        plan_base = calc_base.compute("iron-plate", rate=1.0)
        plan_fast = calc_fast.compute("iron-plate", rate=1.0)
        assert plan_fast.root.machines_needed < plan_base.root.machines_needed


class TestPlanStructure:
    def test_plan_has_target_info(self, calc):
        plan = calc.compute("electronic-circuit", rate=10.0)
        assert plan.target_item == "electronic-circuit"
        assert plan.target_rate == 10.0

    def test_totals_includes_all_items(self, calc):
        plan = calc.compute("electronic-circuit", rate=1.0)
        assert "electronic-circuit" in plan.totals
        assert "iron-plate" in plan.totals
        assert "copper-cable" in plan.totals

    def test_machine_totals_populated(self, calc):
        plan = calc.compute("electronic-circuit", rate=1.0)
        assert len(plan.machine_totals) > 0

    def test_raw_resources_are_terminal(self, calc):
        plan = calc.compute("advanced-circuit", rate=1.0)
        db = RecipeDB()
        for item in plan.raw_resources:
            assert db.get(item) is None


class TestRecipeDB:
    def test_get_known_recipe(self):
        db = RecipeDB()
        r = db.get("iron-plate")
        assert r is not None
        assert r.crafting_time == pytest.approx(3.2)

    def test_get_unknown_returns_none(self):
        db = RecipeDB()
        assert db.get("unobtanium") is None

    def test_list_items_not_empty(self):
        db = RecipeDB()
        items = db.list_items()
        assert len(items) > 20
        assert "electronic-circuit" in items

    def test_add_custom_recipe(self):
        from factorio_planner.models import Recipe
        db = RecipeDB()
        r = Recipe("widget", {"iron-plate": 1}, {"widget": 1}, 1.0)
        db.add(r)
        assert db.get("widget") is not None

    def test_remove_recipe(self):
        db = RecipeDB()
        db.remove("iron-plate")
        assert db.get("iron-plate") is None


class TestFormatter:
    def test_format_plan_returns_string(self, calc):
        from factorio_planner.formatter import format_plan
        plan = calc.compute("electronic-circuit", rate=5.0)
        text = format_plan(plan)
        assert isinstance(text, str)
        assert "electronic-circuit" in text

    def test_format_tree_returns_string(self, calc):
        from factorio_planner.formatter import format_tree
        plan = calc.compute("iron-plate", rate=1.0)
        tree = format_tree(plan.root)
        assert "iron-plate" in tree
        assert "iron-ore" in tree

    def test_to_dict_is_json_serialisable(self, calc):
        import json
        from factorio_planner.formatter import to_dict
        plan = calc.compute("electronic-circuit", rate=2.0)
        d = to_dict(plan)
        json.dumps(d)  # must not raise
        assert d["target_item"] == "electronic-circuit"
