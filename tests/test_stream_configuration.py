import subprocess
import sys
import types
import unittest
from importlib.util import find_spec
from pathlib import Path
from unittest.mock import Mock, patch


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))


@unittest.skipUnless(
    find_spec("fastapi") is not None and find_spec("pydantic") is not None,
    "FastAPI and Pydantic are required for API model tests",
)
class StreamConfigValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        original_modules = {name: sys.modules.pop(name, None) for name in ("api", "analytics", "ingestion", "streaming")}
        sys.modules["analytics"] = types.SimpleNamespace(get_metrics=lambda: {})
        sys.modules["ingestion"] = types.SimpleNamespace(
            start_rtsp_stream=lambda *args: None,
            stop_rtsp_stream=lambda *args: None,
        )
        sys.modules["streaming"] = types.SimpleNamespace(
            start_annotated_stream=lambda *args: None,
            stop_annotated_stream=lambda *args: None,
        )
        import api

        cls.api = api
        for name in ("analytics", "ingestion", "streaming"):
            sys.modules.pop(name, None)
        for name, module in original_modules.items():
            if module is not None:
                sys.modules[name] = module

    def test_stream_config_rejects_invalid_resolution(self):
        with self.assertRaises(ValueError):
            self.api.StreamConfig(stream_name="camera0", source="0", type="raw", resolution="720p")

    def test_stream_update_rejects_non_positive_framerate(self):
        with self.assertRaises(ValueError):
            self.api.StreamUpdate(stream_name="camera0", stream_type="raw", framerate=0)

    def test_stream_config_accepts_positive_dimensions(self):
        config = self.api.StreamConfig(stream_name="camera0", source="0", type="raw", resolution="1280x720")

        self.assertEqual(config.resolution, "1280x720")


class GStreamerCommandTests(unittest.TestCase):
    def test_ingestion_uses_argument_list_without_shell(self):
        import ingestion

        with patch("ingestion.subprocess.Popen") as popen:
            ingestion.start_rtsp_stream("http://camera.local/feed?x=1&y=2", "camera0", "1280x720", is_local=False)

        command = popen.call_args.args[0]
        self.assertIsInstance(command, list)
        self.assertIn("location=http://camera.local/feed?x=1&y=2", command)
        self.assertNotIn("shell", popen.call_args.kwargs)
        self.assertEqual(popen.call_args.kwargs["stdin"], subprocess.PIPE)
        self.assertEqual(popen.call_args.kwargs["stdout"], subprocess.DEVNULL)
        self.assertEqual(popen.call_args.kwargs["stderr"], subprocess.DEVNULL)

    def test_ingestion_accepts_integer_local_camera_source(self):
        import ingestion

        with patch("ingestion.subprocess.Popen") as popen:
            ingestion.start_rtsp_stream(0, "camera0", "1280x720", is_local=True)

        self.assertIn("device-index=0", popen.call_args.args[0])

    def test_bitrate_conversion_accepts_kilobits_and_megabits(self):
        from stream_settings import bitrate_to_kbps

        self.assertEqual(bitrate_to_kbps("750k"), 750)
        self.assertEqual(bitrate_to_kbps("2M"), 2000)

    def test_bitrate_conversion_rejects_invalid_values(self):
        from stream_settings import bitrate_to_kbps

        with self.assertRaises(ValueError):
            bitrate_to_kbps("fast")

    def test_annotated_stream_uses_argument_list_without_shell(self):
        fake_process = types.SimpleNamespace(stdin=types.SimpleNamespace(write=lambda data: None))
        fake_cv2 = types.SimpleNamespace(COLOR_BGR2RGB=1, cvtColor=lambda frame, code: frame)
        fake_numpy = types.SimpleNamespace(
            uint8=object,
            zeros=lambda shape, dtype: types.SimpleNamespace(tobytes=lambda: b""),
        )
        sys.modules.setdefault("cv2", fake_cv2)
        sys.modules.setdefault("numpy", fake_numpy)
        import streaming

        with patch("streaming.subprocess.Popen", return_value=fake_process) as popen:
            streaming.start_annotated_stream("annotated_camera0", 640, 480)

        self.assertIsInstance(popen.call_args.args[0], list)
        self.assertNotIn("shell", popen.call_args.kwargs)
        self.assertEqual(popen.call_args.kwargs["stdout"], subprocess.DEVNULL)
        self.assertEqual(popen.call_args.kwargs["stderr"], subprocess.DEVNULL)


class StreamProcessLifecycleTests(unittest.TestCase):
    def _process(self):
        return types.SimpleNamespace(
            stdin=types.SimpleNamespace(close=lambda: None),
            poll=lambda: None,
            terminate=Mock(),
            wait=Mock(),
            kill=Mock(),
        )

    def test_stopping_annotated_stream_terminates_and_removes_process(self):
        import streaming

        process = self._process()
        streaming.stream_processes["annotated_camera0"] = process

        self.assertTrue(streaming.stop_annotated_stream("annotated_camera0"))
        process.terminate.assert_called_once_with()
        process.wait.assert_called_once_with(timeout=5)
        self.assertNotIn("annotated_camera0", streaming.stream_processes)

    def test_restarting_raw_stream_terminates_existing_process(self):
        import ingestion

        process = self._process()
        ingestion.stream_processes["camera0"] = process
        with patch("ingestion.subprocess.Popen") as popen:
            popen.return_value = self._process()
            ingestion.start_rtsp_stream("0", "camera0", "640x480")

        process.terminate.assert_called_once_with()
        self.assertIs(ingestion.stream_processes["camera0"], popen.return_value)

@unittest.skipUnless(
    find_spec("fastapi") is not None and find_spec("pydantic") is not None,
    "FastAPI and Pydantic are required for API lifecycle tests",
)
class StreamStopEndpointTests(unittest.TestCase):
    def test_stop_endpoint_stops_the_matching_pipeline(self):
        api = StreamConfigValidationTests.api
        api.streams["raw"] = {"camera0": {"status": "active"}}
        with patch.object(api.ingestion, "stop_rtsp_stream") as stop_pipeline:
            api.stop_stream("camera0", "raw")

        stop_pipeline.assert_called_once_with("camera0")
        self.assertEqual(api.streams["raw"]["camera0"]["status"], "inactive")


if __name__ == "__main__":
    unittest.main()
