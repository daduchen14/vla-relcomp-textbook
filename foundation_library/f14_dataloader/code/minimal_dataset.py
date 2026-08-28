"""Day 14 最小版本：自定义 Dataset，并观察 DataLoader 如何拼 batch。"""

import torch
from torch.utils.data import DataLoader, Dataset


class FixtureDataset(Dataset[dict[str, object]]):
    """五条确定性 y=2x+1 教学样本。"""

    def __len__(self) -> int:
        return 5

    def __getitem__(self, index: int) -> dict[str, object]:
        x = torch.tensor([float(index)], dtype=torch.float32)
        y = 2.0 * x + 1.0
        return {"sample_id": f"fixture_sample_{index:03d}", "x": x, "y": y}


torch.manual_seed(7)
dataset = FixtureDataset()
loader = DataLoader(dataset, batch_size=2, shuffle=False)

print("dataset_length", len(dataset))
print("sample_zero", dataset[0])
for batch_index, batch in enumerate(loader):
    print(batch_index, batch["sample_id"], tuple(batch["x"].shape))
print("synthetic dataset; not a VLA experiment result")
