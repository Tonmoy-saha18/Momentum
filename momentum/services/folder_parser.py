"""Scan a local folder tree and persist its course / section / lesson structure."""

from __future__ import annotations

import logging
from pathlib import Path

from momentum.config import Config
from momentum.models.database import Database
from momentum.models.entities import Course, Lesson
from momentum.utils.helpers import natural_sort_key, sanitize_title

logger = logging.getLogger(__name__)


class FolderParser:
    """Parses a root course folder into the database."""

    def __init__(self, db: Database):
        self.db = db

    # ── public API ───────────────────────────────────────────────────

    def parse_course_folder(self, folder_path: str) -> Course:
        """Scan *folder_path*, create a Course with Sections / Lessons, return it."""
        root = Path(folder_path).resolve()
        if not root.is_dir():
            raise ValueError(f"Invalid folder path: {folder_path}")

        existing = self.db.get_course_by_path(str(root))
        if existing:
            raise ValueError(f"Course already loaded: {existing.name}")

        course_name = sanitize_title(root.name) or root.name
        course = Course(name=course_name, root_path=str(root))
        course_id = self.db.insert_course(course)
        course.id = course_id

        subdirs = self._sorted_dirs(root)
        root_videos = self._find_videos(root)
        lesson_count = 0

        if subdirs:
            for idx, section_dir in enumerate(subdirs):
                section_id = self.db.insert_section(
                    course_id=course_id,
                    name=sanitize_title(section_dir.name) or section_dir.name,
                    order_index=idx,
                    folder_path=str(section_dir),
                )
                lesson_count += self._insert_videos(section_dir, section_id, course_id)

            if root_videos:
                section_id = self.db.insert_section(
                    course_id=course_id,
                    name="General",
                    order_index=len(subdirs),
                    folder_path=str(root),
                )
                lesson_count += self._insert_video_list(root_videos, section_id, course_id)

        elif root_videos:
            section_id = self.db.insert_section(
                course_id=course_id,
                name=course_name,
                order_index=0,
                folder_path=str(root),
            )
            lesson_count += self._insert_video_list(root_videos, section_id, course_id)

        else:
            lesson_count += self._parse_recursive(root, course_id, order_offset=0)

        self.db.update_course_progress(course_id)
        course = self.db.get_course(course_id)  # type: ignore[assignment]
        logger.info("Parsed course '%s' — %d lessons", course_name, lesson_count)
        return course  # type: ignore[return-value]

    # ── private helpers ──────────────────────────────────────────────

    def _sorted_dirs(self, directory: Path) -> list[Path]:
        return sorted(
            (d for d in directory.iterdir() if d.is_dir() and not d.name.startswith(".")),
            key=lambda d: natural_sort_key(d.name),
        )

    def _find_videos(self, directory: Path) -> list[Path]:
        videos = [
            f
            for f in directory.iterdir()
            if f.is_file() and f.suffix.lower() in Config.VIDEO_EXTENSIONS
        ]
        return sorted(videos, key=lambda f: natural_sort_key(f.name))

    def _insert_videos(self, directory: Path, section_id: int, course_id: int) -> int:
        return self._insert_video_list(self._find_videos(directory), section_id, course_id)

    def _insert_video_list(self, videos: list[Path], section_id: int, course_id: int) -> int:
        for idx, video_path in enumerate(videos):
            self.db.insert_lesson(
                Lesson(
                    section_id=section_id,
                    course_id=course_id,
                    title=sanitize_title(video_path.name),
                    file_path=str(video_path),
                    order_index=idx,
                )
            )
        return len(videos)

    def _parse_recursive(self, directory: Path, course_id: int, order_offset: int) -> int:
        total = 0
        subdirs = self._sorted_dirs(directory)
        for idx, subdir in enumerate(subdirs):
            videos = self._find_videos(subdir)
            if videos:
                section_id = self.db.insert_section(
                    course_id=course_id,
                    name=sanitize_title(subdir.name) or subdir.name,
                    order_index=order_offset + idx,
                    folder_path=str(subdir),
                )
                total += self._insert_video_list(videos, section_id, course_id)
            total += self._parse_recursive(subdir, course_id, order_offset + len(subdirs))
        return total
