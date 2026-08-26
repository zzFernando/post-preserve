from pathlib import Path

from postpreserve.capture.browsertrix import BrowsertrixBackend


def test_capture_uses_absolute_host_path_for_docker_volume(monkeypatch, tmp_path: Path):
    command = []

    def fake_run(cmd, **kwargs):
        command.extend(cmd)
        capture_dir = Path(cmd[cmd.index("--cwd") + 1])
        host_dir = Path(cmd[cmd.index("-v") + 1].rsplit(":", 1)[0])
        assert capture_dir == Path("/capture")
        generated = host_dir / "collections/post/post.wacz"
        generated.parent.mkdir(parents=True)
        generated.write_bytes(b"wacz")

    monkeypatch.setattr("postpreserve.capture.browsertrix.subprocess.run", fake_run)
    monkeypatch.chdir(tmp_path.parent)
    relative_workdir = Path(tmp_path.name) / "capture"

    BrowsertrixBackend().capture(
        url="https://www.instagram.com/p/EXAMPLE/",
        workdir=relative_workdir,
        timeout_seconds=30,
        headed=False,
        browser_profile=None,
    )

    mount = command[command.index("-v") + 1]
    host_path, container_path = mount.rsplit(":", 1)
    assert Path(host_path).is_absolute()
    assert container_path == "/capture"
    assert command[command.index("--url") + 1] == "https://www.instagram.com/p/EXAMPLE/"
    assert "--output" not in command
    assert (Path(host_path) / "post.wacz").read_bytes() == b"wacz"
