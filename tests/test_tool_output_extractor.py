"""Tests for tool output extractor."""

import pytest

from utils.tool_output_extractor import ToolOutputExtractor


class TestToolOutputExtractor:
    """Tests for ToolOutputExtractor class."""

    def test_extract_unknown_tool_returns_empty(self):
        """Test unknown tool returns empty result."""
        output_type, metadata = ToolOutputExtractor.extract(
            "unknown_tool", {}, {}
        )
        assert output_type == ""
        assert metadata == {}

    def test_register_decorator(self):
        """Test register decorator adds extractor."""
        # Clean up any existing registration
        original = ToolOutputExtractor.EXTRACTORS.copy()

        @ToolOutputExtractor.register("test_tool_123")
        def test_extractor(args, result):
            return "test", {"key": "value"}

        assert "test_tool_123" in ToolOutputExtractor.EXTRACTORS

        # Test the extractor works
        output_type, metadata = ToolOutputExtractor.extract(
            "test_tool_123", {}, {}
        )
        assert output_type == "test"
        assert metadata == {"key": "value"}

        # Clean up
        ToolOutputExtractor.EXTRACTORS = original


class TestDiffExtractor:
    """Tests for diff/file edit extractor."""

    @pytest.mark.parametrize("tool_name", ["edit_file", "write_file", "create_file"])
    def test_extracts_diff(self, tool_name: str):
        """Test diff extraction from file edit tools."""
        result = {
            "diff": "--- a/file.py\n+++ b/file.py\n@@ -1 +1 @@\n-old\n+new",
            "operation": "modify",
            "path": "/path/to/file.py",
        }

        output_type, metadata = ToolOutputExtractor.extract(
            tool_name, {"file_path": "/path/to/file.py"}, result
        )

        assert output_type == "diff"
        assert metadata["diff_text"] == result["diff"]
        assert metadata["operation"] == "modify"
        assert metadata["filepath"] == "/path/to/file.py"

    def test_returns_empty_when_no_diff(self):
        """Test returns empty when result has no diff."""
        output_type, metadata = ToolOutputExtractor.extract(
            "edit_file", {}, {"success": True}
        )
        assert output_type == ""
        assert metadata == {}


class TestShellExtractor:
    """Tests for shell command extractor."""

    @pytest.mark.parametrize("tool_name", ["run_shell_command", "execute_command", "shell", "bash"])
    def test_extracts_shell_dict_result(self, tool_name: str):
        """Test shell extraction from dict result."""
        result = {
            "output": "Hello World",
            "exit_code": 0,
            "cwd": "/home/user",
        }

        output_type, metadata = ToolOutputExtractor.extract(
            tool_name, {"command": "echo Hello World"}, result
        )

        assert output_type == "shell"
        assert metadata["command"] == "echo Hello World"
        assert metadata["output"] == "Hello World"
        assert metadata["exit_code"] == 0
        assert metadata["cwd"] == "/home/user"

    def test_extracts_shell_string_result(self):
        """Test shell extraction from string result."""
        output_type, metadata = ToolOutputExtractor.extract(
            "bash", {"command": "ls"}, "file1.txt\nfile2.txt"
        )

        assert output_type == "shell"
        assert metadata["output"] == "file1.txt\nfile2.txt"
        assert metadata["exit_code"] == 0

    def test_handles_stdout_key(self):
        """Test handles 'stdout' key as alternative to 'output'."""
        result = {"stdout": "output text", "return_code": 1}

        output_type, metadata = ToolOutputExtractor.extract(
            "shell", {"command": "test"}, result
        )

        assert metadata["output"] == "output text"
        assert metadata["exit_code"] == 1


class TestFileListingExtractor:
    """Tests for directory listing extractor."""

    @pytest.mark.parametrize("tool_name", ["list_directory", "list_files", "ls"])
    def test_extracts_file_listing(self, tool_name: str):
        """Test file listing extraction."""
        result = {
            "entries": ["file1.txt", "file2.py", "subdir/"],
            "total_size": 1024,
            "dir_count": 1,
            "file_count": 2,
        }

        output_type, metadata = ToolOutputExtractor.extract(
            tool_name, {"path": "/home/user"}, result
        )

        assert output_type == "file_listing"
        assert metadata["directory"] == "/home/user"
        assert metadata["entries"] == ["file1.txt", "file2.py", "subdir/"]
        assert metadata["total_size"] == 1024

    def test_handles_files_key(self):
        """Test handles 'files' key as alternative to 'entries'."""
        result = {"files": ["a.txt", "b.txt"]}

        output_type, metadata = ToolOutputExtractor.extract(
            "ls", {"directory": "."}, result
        )

        assert metadata["entries"] == ["a.txt", "b.txt"]


class TestGrepExtractor:
    """Tests for grep/search extractor."""

    @pytest.mark.parametrize("tool_name", ["grep", "search_files", "search", "find_in_files"])
    def test_extracts_grep_results(self, tool_name: str):
        """Test grep extraction."""
        result = {
            "matches": [
                {"file": "a.py", "line": 10, "content": "def foo():"},
                {"file": "b.py", "line": 20, "content": "def foo():"},
            ],
            "total_matches": 2,
        }

        output_type, metadata = ToolOutputExtractor.extract(
            tool_name, {"pattern": "def foo", "path": "/src"}, result
        )

        assert output_type == "grep"
        assert metadata["search_term"] == "def foo"
        assert metadata["directory"] == "/src"
        assert len(metadata["matches"]) == 2
        assert metadata["total_matches"] == 2

    def test_handles_results_key(self):
        """Test handles 'results' key as alternative to 'matches'."""
        result = {"results": [{"file": "x.py"}]}

        output_type, metadata = ToolOutputExtractor.extract(
            "grep", {"query": "test"}, result
        )

        assert metadata["matches"] == [{"file": "x.py"}]
        assert metadata["search_term"] == "test"


class TestFileHeaderExtractor:
    """Tests for file read header extractor."""

    @pytest.mark.parametrize("tool_name", ["read_file", "view_file", "cat"])
    def test_extracts_file_header(self, tool_name: str):
        """Test file header extraction."""
        output_type, metadata = ToolOutputExtractor.extract(
            tool_name, {"file_path": "/path/to/file.py"}, "file content"
        )

        assert output_type == "file_header"
        assert metadata["filepath"] == "/path/to/file.py"

    def test_includes_line_range(self):
        """Test includes line range info when provided."""
        output_type, metadata = ToolOutputExtractor.extract(
            "read_file",
            {"file_path": "/file.py", "start_line": 10, "end_line": 20},
            "content"
        )

        assert "10" in metadata["line_info"]
        assert "20" in metadata["line_info"]

    def test_returns_empty_when_no_path(self):
        """Test returns empty when no file path."""
        output_type, metadata = ToolOutputExtractor.extract(
            "read_file", {}, "content"
        )
        assert output_type == ""


class TestSkillExtractors:
    """Tests for skill-related extractors."""

    def test_extracts_skill_list(self):
        """Test skill list extraction."""
        result = {
            "skills": [{"name": "skill1"}, {"name": "skill2"}],
            "total_count": 2,
            "query": "test",
        }

        output_type, metadata = ToolOutputExtractor.extract(
            "list_or_search_skills", {}, result
        )

        assert output_type == "skill_list"
        assert len(metadata["skills"]) == 2
        assert metadata["total_count"] == 2

    def test_extracts_skill_activate(self):
        """Test skill activation extraction."""
        result = {
            "skill_name": "my_skill",
            "content": "Skill content here",
            "resources": ["/path/to/resource"],
        }

        output_type, metadata = ToolOutputExtractor.extract(
            "activate_skill", {"skill_name": "my_skill"}, result
        )

        assert output_type == "skill_activate"
        assert metadata["skill_name"] == "my_skill"
        assert metadata["content"] == "Skill content here"
        assert metadata["resources"] == ["/path/to/resource"]

    def test_handles_pydantic_model(self):
        """Test handles Pydantic model results."""
        class MockModel:
            def model_dump(self):
                return {"skills": [], "total_count": 0}

        output_type, metadata = ToolOutputExtractor.extract(
            "list_or_search_skills", {}, MockModel()
        )

        assert output_type == "skill_list"
