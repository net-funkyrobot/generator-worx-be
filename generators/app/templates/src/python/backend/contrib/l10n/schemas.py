from typing import Dict

from pydantic import BaseModel


class FsNames(BaseModel):
    en: str
    l10n: Dict[str, str]
