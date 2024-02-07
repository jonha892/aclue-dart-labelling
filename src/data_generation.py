from dataclasses import dataclass
import math
import random
from typing import List, Tuple
import os

from PIL import Image

from src.draw_util import composite_at


@dataclass
class Position:
    x: int
    y: int


@dataclass
class Annotation:
    pos: Position
    label: str


@dataclass
class OutLabel:
    image_path: str
    series_id: int
    annotations: [Annotation]

    def to_json(self):
        return {
            "image_path": self.image_path,
            "series_id": self.series_id,
            "annotations": list(map(lambda x: x.__dict__, self.annotations)),
        }


@dataclass
class DartConfig:
    id: int
    darts: List[Tuple[Image.Image, Tuple[int, int]]]


@dataclass
class DataGenerationConfig:
    number_of_throw_sequences: int
    position_configs: Tuple[dict[str, any], dict[str, any], dict[str, any]]


class PositionGenerator:
    def __init__(
        self,
        center: Position,
        anchor_top: Position,
        anchor_bottom: Position,
        anchor_left: Position,
        anchor_right: Position,
        bounds_offset=30,
    ) -> None:
        self.center = center

        self.anchor_top = anchor_top
        self.anchor_bottom = anchor_bottom
        self.anchor_left = anchor_left
        self.anchor_right = anchor_right

        self.bounds_offset = bounds_offset

        total_width = anchor_right.x - anchor_left.x
        total_height = anchor_bottom.y - anchor_top.y
        self.max_radius = (total_height + total_width) / 4

    def radius_rel_to_abs(self, radius: float) -> int:
        # radius is relative to the center
        if radius > 1 or radius < 0:
            raise ValueError("radius must be between 0 and 1")
        return int(radius * self.max_radius)

    @staticmethod
    def generate_random_with_radius_at(
        radius_abs: int, start: Tuple[int, int]
    ) -> Tuple[int, int]:
        angle = random.random() * 2 * math.pi
        x = start[0] + radius_abs * math.sin(math.radians(angle))
        y = start[1] - radius_abs * math.cos(math.radians(angle))
        x = int(x)
        y = int(y)
        print(f'start {start}, generated ({x}{y}) angle {angle} radius {radius_abs}')
        return (x, y)

    def generate(self, opt: dict[str, any]) -> Position:
        type = opt["type"]
        if type == "random":
            offset = self.bounds_offset
            return Position(
                random.randint(
                    self.anchor_left.x - offset, self.anchor_right.x + offset
                ),
                random.randint(
                    self.anchor_top.y - offset, self.anchor_bottom.y + offset
                ),
            )
        if type == "radius":
            if (
                not "radius" in opt
                or not "angle" in opt
                or not "selection_radius_abs" in opt
            ):
                raise ValueError("radius, angle, and selection_radius_abs must be provided")
            radius = opt["radius"]
            radius = self.radius_rel_to_abs(radius)
            angle = opt["angle"]
            selection_radius_abs = opt["selection_radius_abs"]

            start_x = self.center.x + radius * math.sin(math.radians(angle))
            start_y = self.center.y - radius * math.cos(math.radians(angle))
            point = self.generate_random_with_radius_at(
                selection_radius_abs, (start_x, start_y)
            )
            return Position(point[0], point[1])
        else:
            raise ValueError("type must be either random or radius")


class DataGenerator:
    def __init__(
        self,
        anchor_top: Position,
        anchor_bottom: Position,
        anchor_left: Position,
        anchor_right: Position,
        position_generator,
    ) -> None:
        self.anchors = [anchor_top, anchor_bottom, anchor_left, anchor_right]
        self.anchors = list(map(lambda x: (x, "anchor"), self.anchors))

        self.position_generator = position_generator

    def generate(
        self,
        position_config: List[DataGenerationConfig],
        darts: List[DartConfig],
        dartboard: Image,
        out_path: str,
    ) -> List[OutLabel]:
        # create dir if not exist
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        padding = len(str(len(position_config) -1))

        out_labels = []

        for c, config in enumerate(position_config):
            print(f'{c} - position config: {config.position_configs}')
            for i in range(config.number_of_throw_sequences):
                print("processing throw sequence: ", i)

                # select dart type for throw sequence
                dart_config = darts[random.randint(0, len(darts) - 1)]
                selected_darts = random.sample(dart_config.darts, 3)

                tmp_annotations = []
                composite = dartboard
                for j, dart in enumerate(selected_darts):
                    dart_img, dart_top_pos = dart
                    position = self.position_generator.generate(config.position_configs[j])
                    composite = composite_at(composite, dart_img, (position.x, position.y))
                    dart_out_path = f"{out_path}/dart_{c:0{padding}}_{i:0{2}}_{j}.png"
                    composite.save(dart_out_path)

                    position = Position(dart_top_pos[0] + position.x, dart_top_pos[1] + position.y)
                    tmp_annotations += [Annotation(position, "dart")]
                    dart_annotations = [*tmp_annotations, *self.anchors]

                    out_labels += [OutLabel(dart_out_path, i, dart_annotations)]
        return out_labels
