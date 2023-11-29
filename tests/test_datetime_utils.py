import pytest
from datetime import datetime, date, time, timedelta
import pendulum
import time as pytime
from misc_utils import DateTimeUtils, StopWatch


class TestDateTimeUtils:
    @pytest.fixture
    def dt_utils_default(self):
        return DateTimeUtils()

    @pytest.fixture
    def dt_utils_custom(self):
        return DateTimeUtils("%d/%m/%Y %H:%M:%S")

    # Tests for extract_format
    @pytest.mark.parametrize(
        "datetime_format, expected_date_format, expected_time_format",
        [
            ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%H:%M:%S"),
            ("%Y-%m-%d", "%Y-%m-%d", None),
            ("%H:%M:%S", None, "%H:%M:%S"),
            ("%d-%b-%Y %I:%M %p", "%d-%b-%Y", "%I:%M %p"),
        ],
    )
    def test_extract_format(
        self, datetime_format, expected_date_format, expected_time_format
    ):
        dt_utils = DateTimeUtils(datetime_format)
        assert dt_utils.date_format == expected_date_format
        assert dt_utils.time_format == expected_time_format

    @pytest.mark.parametrize(
        "datetime_format, expected_date_format, expected_time_format",
        [
            ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%H:%M:%S"),
            ("%Y-%m-%d", "%Y-%m-%d", None),
            ("%H:%M:%S", None, "%H:%M:%S"),
        ],
    )
    def test_constructor(
        self, datetime_format, expected_date_format, expected_time_format
    ):
        dt_utils = DateTimeUtils(datetime_format)
        assert dt_utils.datetime_format == datetime_format
        assert dt_utils.date_format == expected_date_format
        assert dt_utils.time_format == expected_time_format

    # ... Convert string to datetime, date or time ...
    @pytest.mark.parametrize(
        "input_str, expected_output",
        [
            ("2022-01-01 12:00:00", datetime(2022, 1, 1, 12, 0, 0)),
            ("01/01/2022 12:00:00", datetime(2022, 1, 1, 12, 0, 0)),
        ],
    )
    def test_datetime_from_string(
        self, dt_utils_default, dt_utils_custom, input_str, expected_output
    ):
        assert dt_utils_default.datetime_from_string(input_str) == expected_output
        assert dt_utils_custom.datetime_from_string(input_str) == expected_output

    @pytest.mark.parametrize(
        "input_str, expected_output", [("2022-01-01", date(2022, 1, 1))]
    )
    def test_date_from_string(self, dt_utils_default, input_str, expected_output):
        assert dt_utils_default.date_from_string(input_str) == expected_output

    @pytest.mark.parametrize(
        "datetime_format, input_str",
        [
            ("%H:%M:%S", "2022-01-01"),
        ],
    )
    def test_date_from_string_raises(self, datetime_format, input_str):
        dt_utils = DateTimeUtils(datetime_format)
        with pytest.raises(ValueError):
            dt_utils.date_from_string(input_str)

    @pytest.mark.parametrize(
        "datetime_format, input_str, expected_output",
        [
            ("%H:%M:%S", "12:00:00", time(12, 0)),
            ("%I:%M %p", "12:00 PM", time(12, 0)),
        ],
    )
    def test_time_from_string(self, datetime_format, input_str, expected_output):
        dt_utils = DateTimeUtils(datetime_format)
        assert dt_utils.time_from_string(input_str) == expected_output

    def test_time_from_string_raises(self):
        dt_utils = DateTimeUtils("%Y-%m-%d")
        with pytest.raises(ValueError):
            dt_utils.time_from_string("2022-01-01 12:00:00")

    @pytest.mark.parametrize(
        "datetime_format, input_dt, expected_output",
        [
            ("%Y-%m-%d %H:%M:%S", datetime(2022, 1, 1, 12, 0), "2022-01-01 12:00:00"),
            ("%d-%m-%Y %I:%M %p", datetime(2022, 1, 1, 12, 0), "01-01-2022 12:00 PM"),
        ],
    )
    def test_string_from_datetime(self, datetime_format, input_dt, expected_output):
        dt_utils = DateTimeUtils(datetime_format)
        assert dt_utils.string_from_datetime(input_dt) == expected_output

    @pytest.mark.parametrize(
        "date_format, input_date, expected_output",
        [
            ("%Y-%m-%d", date(2022, 1, 1), "2022-01-01"),
            ("%d-%m-%Y", date(2022, 1, 1), "01-01-2022"),
        ],
    )
    def test_string_from_date(self, date_format, input_date, expected_output):
        dt_utils = DateTimeUtils(datetime_format=date_format)
        assert dt_utils.string_from_date(input_date) == expected_output

    def test_string_from_date_raises(self):
        dt_utils = DateTimeUtils(datetime_format="%H:%M:%S")
        with pytest.raises(ValueError):
            dt_utils.string_from_date(date(2022, 1, 1))

    @pytest.mark.parametrize(
        "time_format, input_time, expected_output",
        [
            ("%H:%M:%S", time(12, 0), "12:00:00"),
            ("%I:%M %p", time(12, 0), "12:00 PM"),
        ],
    )
    def test_string_from_time(self, time_format, input_time, expected_output):
        dt_utils = DateTimeUtils(datetime_format=time_format)
        assert dt_utils.string_from_time(input_time) == expected_output

    def test_string_from_time_raises(self):
        dt_utils = DateTimeUtils(datetime_format="%Y-%m-%d")
        with pytest.raises(ValueError):
            dt_utils.string_from_time(time(12, 0))

    def test_now(self, dt_utils_default):
        assert isinstance(dt_utils_default.now(), datetime)

    @pytest.mark.parametrize(
        "years, days, hours, minutes, seconds, microseconds, expected_relation",
        [
            (1, 0, 0, 0, 0, 0, "greater"),
            (-1, 0, 0, 0, 0, 0, "less"),
            # Add more test cases as needed
        ],
    )
    def test_time_from_now(
        self,
        dt_utils_default,
        years,
        days,
        hours,
        minutes,
        seconds,
        microseconds,
        expected_relation,
    ):
        future_time = dt_utils_default.time_from_now(
            years, days, hours, minutes, seconds, microseconds
        )
        now = pendulum.now()

        if expected_relation == "greater":
            assert future_time > now
        elif expected_relation == "less":
            assert future_time < now


class TestStopWatch:
    @pytest.fixture
    def non_running_stopwatch(self):
        return StopWatch(time_format = "%Hh %Mm %Ss", start_on_init=False)

    @pytest.fixture
    def running_stopwatch(self):
        sw = StopWatch(time_format = "%Hh %Mm %Ss", start_on_init=False)

        # We'll "mock" this to show that it runs for 1 second
        sw._start_time = pendulum.now()
        sw._elapsed = timedelta(seconds=1)

        return sw

    # ... Start tests ...
    def test_constructor(self, non_running_stopwatch):
        assert non_running_stopwatch._start_time is None
        assert non_running_stopwatch._elapsed == timedelta(0)

    def test_start(self, non_running_stopwatch):
        non_running_stopwatch.start()
        assert non_running_stopwatch._start_time is not None

    def test_start_raises(self, running_stopwatch):
        with pytest.raises(RuntimeError):
            running_stopwatch.start()

    def test_stop(self, running_stopwatch):
        running_stopwatch.stop()
        assert running_stopwatch._start_time is None
        assert running_stopwatch._elapsed > timedelta(0)

    def test_stop_raises(self, non_running_stopwatch):
        with pytest.raises(RuntimeError):
            non_running_stopwatch.stop()

    def test_reset(self, running_stopwatch):
        running_stopwatch.reset()
        assert running_stopwatch._start_time is None
        assert running_stopwatch._elapsed == timedelta(0)

    def test_elapsed_time(self, running_stopwatch):
        elapsed = running_stopwatch.elapsed_time
        assert elapsed >= timedelta(seconds=1)

    def test__str__(self, running_stopwatch):
        assert str(running_stopwatch) == '00h 00m 01s'

    # ... For comparison, just test __eq__ and __lt__ ...
    # ... __gt__, __le__, __ge__, and __ne__ are just the inverse of the above two ...
    def test__eq__(self):
        stopwatch1 = StopWatch(time_format="%Hh %Mm %Ss", start_on_init=False)
        stopwatch1._elapsed = timedelta(seconds=1)

        stopwatch2 = StopWatch(time_format="%Hh %Mm %Ss", start_on_init=False)
        stopwatch2._elapsed = timedelta(seconds=1)

        assert stopwatch1 == stopwatch2
        assert stopwatch1 == timedelta(seconds=1)
        assert stopwatch1 == 1
        assert stopwatch1 == 1.0


    def test__lt__(self, running_stopwatch):
        second_running_stopwatch = StopWatch(time_format = "%Hh %Mm %Ss", start_on_init=False)
        second_running_stopwatch._start_time = pendulum.now()
        second_running_stopwatch._elapsed = timedelta(seconds=2)

        assert running_stopwatch < second_running_stopwatch
        assert running_stopwatch < timedelta(seconds=2)
        assert running_stopwatch < 2
        assert running_stopwatch < 2.0


if __name__ == "__main__":
    from pathlib import Path
    from pprint import pprint
    import pytest

    test_file = Path(__file__).absolute()
    test_class_or_function = None
    test_method = None

    # test_class_or_function = "TestStopWatch"
    # test_method = "test__str__"

    test_path = test_file
    if test_class_or_function is not None:
        test_path = f"{test_path}::{test_class_or_function}"
    if test_method is not None:
        test_path = f"{test_path}::{test_method}"

    args = [
        test_path,
        "-s",
        "--verbose",
    ]

    pytest.main(args)
