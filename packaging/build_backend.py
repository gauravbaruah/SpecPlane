"""PEP 517 backend: copy the kit into the wheel so `uvx specplane init` works."""

from __future__ import annotations

from setuptools.build_meta import (  # noqa: F401
    build_editable as _build_editable,
    build_sdist as _build_sdist,
    build_wheel as _build_wheel,
    get_requires_for_build_editable,
    get_requires_for_build_sdist,
    get_requires_for_build_wheel,
    prepare_metadata_for_build_editable,
    prepare_metadata_for_build_wheel,
)

from bundle_kit import BUNDLE, populate_bundle


def _ensure_package() -> None:
    BUNDLE.mkdir(parents=True, exist_ok=True)
    init = BUNDLE / "__init__.py"
    if not init.exists():
        init.write_text("", encoding="utf-8")


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    populate_bundle()
    return _build_wheel(wheel_directory, config_settings, metadata_directory)


def build_sdist(sdist_directory, config_settings=None):
    populate_bundle()
    return _build_sdist(sdist_directory, config_settings)


def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    _ensure_package()
    return _build_editable(wheel_directory, config_settings, metadata_directory)
