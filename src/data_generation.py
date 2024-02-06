from dataclasses import dataclass
import math
import random
from typing import Tuple

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
    darts: [Image]


@dataclass
class DataGenerationConfig:
    position_config: dict
    number_of_throw: int


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

        total_width = (anchor_right.x - anchor_left.x)
        total_height = (anchor_bottom.y - anchor_top.y)
        self.max_radius = (total_height + total_width) / 4

    def radius_to_bounds(self, radius: float) -> int:
        # radius is relative to the center
        if radius > 1 or radius < 0:
            raise ValueError("radius must be between 0 and 1")
        return int(radius * self.max_radius)

    @staticmethod
    def generate_random_with_radius_at(
        radius: int, start: Tuple[int, int]
    ) -> Tuple[int, int]:
        angle = random.random() * 2 * math.pi
        x = start[0] + radius * math.cos(angle)
        y = start[1] + radius * math.sin(angle)
        return (x, y)

    def generate(self, opt: dict[str, any]) -> Position:
        type = opt["type"]
        if type == "random":
            offset = self.bounds_offset
            return Position(
                random.randint(
                    self.anchor_left[0] - offset, self.anchor_right[0] + offset
                ),
                random.randint(
                    self.anchor_top[1] - offset, self.anchor_bottom[1] + offset
                ),
            )
        if type == "radius":
            if (
                not "radius" in opt
                or not "angle" in opt
                or not "selection_radius" in opt
            ):
                raise ValueError("radius, angle, and selection_radius must be provided")
            radius = opt["radius"]
            radius = self.radius_to_bounds(radius)
            angle = opt["angle"]
            selection_radius = opt["selection_radius"]
            selection_radius = self.radius_to_bounds(selection_radius)

            start_x = self.center.x + radius * math.cos(angle)
            start_y = self.center.y + radius * math.sin(angle)
            point = self.generate_random_with_radius_at(
                selection_radius, (start_x, start_y)
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
        position_config: [DataGenerationConfig],
        darts: DartConfig,
        dartboard: Image,
        out_path: str,
    ) -> [OutLabel]:
        out_labels = []

        for config in position_config:
            print("processing config: ", config)
            for i in range(config.number_of_throw):
                print("processing throw: ", i)

                # select dart randomly
                dart_config = darts[random.randint(0, len(self.darts) - 1)]
                darts = random.sample(dart_config.darts, 3)

                tmp_annotations = []
                for dart, j in enumerate(darts):
                    position = self.position_generator.generate(config.position_config)
                    composite_at(dartboard, dart, position)
                    dart_out_path = f"{out_path}/dart_{i}_{j}.png"
                    dart.save(dart_out_path)

                    tmp_annotations += [Annotation(position, "dart")]
                    dart_annotations = [*tmp_annotations, *self.anchors]

                    out_labels += [OutLabel(dart_out_path, i, dart_annotations)]
        return out_labels
