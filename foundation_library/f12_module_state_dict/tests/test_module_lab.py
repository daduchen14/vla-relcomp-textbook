"""Day 12 测试：参数注册、训练和 checkpoint round-trip。"""

import tempfile
import unittest
from pathlib import Path

import torch

from foundation_library.f12_module_state_dict.code.module_lab import (
    ModuleContractError,
    initialize_model,
    load_state_dict,
    make_fixture_data,
    parameter_manifest,
    predict,
    save_state_dict,
    train_model,
)


class ModuleLabTests(unittest.TestCase):
    def test_linear_parameters_are_registered(self) -> None:
        model = initialize_model(7)
        names = [item["name"] for item in parameter_manifest(model)]
        self.assertEqual(names, ["linear.weight", "linear.bias"])

    def test_module_training_reduces_loss(self) -> None:
        features, targets = make_fixture_data()
        model = initialize_model(7)
        history = train_model(model, features, targets, 0.1, 100)
        self.assertLess(history[-1].loss, history[0].loss)
        self.assertAlmostEqual(float(model.linear.weight.detach().squeeze()), 2.0, places=4)
        self.assertAlmostEqual(float(model.linear.bias.detach().squeeze()), 1.0, places=4)

    def test_state_dict_round_trip_preserves_predictions(self) -> None:
        features, targets = make_fixture_data()
        model = initialize_model(7)
        train_model(model, features, targets, 0.1, 20)
        before = predict(model, features)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture_state.pt"
            save_state_dict(model, path)
            after = predict(load_state_dict(path), features)
        self.assertTrue(torch.equal(before, after))

    def test_wrong_feature_shape_is_rejected(self) -> None:
        model = initialize_model(7)
        with self.assertRaisesRegex(ModuleContractError, r"\(N,1\)"):
            model(torch.zeros(3, dtype=torch.float64))


if __name__ == "__main__":
    unittest.main()
