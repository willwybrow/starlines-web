import re
import uuid
from uuid import UUID

from colour import Color


class ID(UUID):
    @property
    def name(self) -> str:
        return re.sub("\d", "", self.hex).title()

    @property
    def colour(self) -> Color:
        return Color(hue=float(self.bytes[0])/255, saturation=1.0, luminance=0.9)