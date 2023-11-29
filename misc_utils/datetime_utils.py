from datetime import datetime, timedelta
from typing import List, Optional, Union

import dateparser
import pendulum

try:
    from .decorator_utils import export
except ImportError:
    from decorator_utils import export


@export
class DateTimeUtils:
    """
    Utility class for converting between different datetime formats.

    Does not handle edge cases like timezones, leap years, etc.
    """

    # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
    DATE_DIRECTIVES = [f"%{d}" for d in "aAbBcdjUmwyY"]
    TIME_DIRECTIVES = [f"%{d}" for d in "HIklMpPrRsSTXzZ"]

    @staticmethod
    def extract_format(directives: List[str], datetime_format: str) -> Optional[str]:
        """
        Extracts a substring containing all the directives with their separators from a datetime format string.

        Parameters:
            directives (List[str]): A list of format directives (e.g., ['%Y', '%m', '%d']).
            datetime_format (str): The datetime format string from which to extract the directives.

        Returns:
            Optional[str]: A substring of the datetime_format that contains the directives and their separators.
            If none of the directives are found, returns None.

        The function identifies the positions of the first and last directive within the datetime_format string.
        It then extracts the substring from the datetime_format that includes all the directives in sequence,
        preserving the separators. This assumes that all date or time directives form a contiguous block in the
        datetime_format. If the directives are intermingled with other content, the result may be incorrect.
        """
        directive_positions = [
            datetime_format.find(d) for d in directives if d in datetime_format
        ]
        if not directive_positions:
            return None

        start, end = min(directive_positions), max(directive_positions)
        return datetime_format[start : end + 2]

    def __init__(
        self,
        datetime_format: str = "%Y-%m-%d %H:%M:%S",
        # datetime_format: str = "%a %b %d %Y, %I:%M%p"
    ):
        """
        Used to determine datetime, date and time formats.
        """

        self.datetime_format = datetime_format
        self.date_format = self.extract_format(self.DATE_DIRECTIVES, datetime_format)
        self.time_format = self.extract_format(self.TIME_DIRECTIVES, datetime_format)

    # ... Convert string to datetime, date or time ...
    def datetime_from_string(self, string: str) -> datetime:
        return dateparser.parse(string, date_formats=[self.datetime_format])

    def date_from_string(self, string: str) -> datetime.date:
        if self.date_format is None:
            raise ValueError("No date format specified.")

        dt = self.datetime_from_string(string)
        return dt.date() if dt else None

    def time_from_string(self, string: str) -> datetime.time:
        if self.time_format is None:
            raise ValueError("No time format specified.")

        dt = self.datetime_from_string(string)
        return dt.time() if dt else None

    # ... Convert datetime, date or time to string given the instance format ...
    def string_from_datetime(self, dt: datetime) -> str:
        return dt.strftime(self.datetime_format)

    def string_from_date(self, date: datetime.date) -> str:
        if self.date_format is None:
            raise ValueError("No date format specified.")

        return date.strftime(self.date_format)

    def string_from_time(self, time: datetime.time) -> str:
        if self.time_format is None:
            raise ValueError("No time format specified.")

        return time.strftime(self.time_format)

    # ... Convert short-hand ...
    dt_from_str = datetime_from_string
    date_from_str = date_from_string
    time_from_str = time_from_string

    str_from_dt = string_from_datetime
    str_from_date = string_from_date
    str_from_time = string_from_time

    # ... Get time ...
    def now(self, dt=True, date=False, time=False) -> datetime:
        """
        Get the current datetime, date, or time.
        """
        now = pendulum.now()
        if dt:
            return now
        elif date:
            return now.date()
        elif time:
            return now.time()
        else:
            return None

    def time_from_now(
        self,
        year: int = 0,
        day: int = 0,
        hour: int = 0,
        minute: int = 0,
        seconds: int = 0,
        microseconds: int = 0,
    ) -> datetime:
        """
        Get a future datetime based on the current time and the provided duration.
        """
        return pendulum.now().add(
            years=year,
            days=day,
            hours=hour,
            minutes=minute,
            seconds=seconds,
            microseconds=microseconds,
        )


@export
class StopWatch:
    """
    Stopwatch utility for measuring elapsed time.
    """

    def __init__(self, time_format: str = "%Hh %Mm %Ss", start_on_init: bool = True):
        self.time_format = time_format
        self._start_time = None
        self._elapsed = timedelta(0)

        if start_on_init:
            self.start()

    def start(self):
        """
        Start the stopwatch. If it is already running, raises a RuntimeError.
        """
        if self._start_time is not None:
            raise RuntimeError("Stopwatch is already running.")

        self._elapsed = timedelta(0)
        self._start_time = pendulum.now()

    def stop(self):
        """
        Stop the stopwatch. If it's not running, raises a RuntimeError.
        """
        if self._start_time is None:
            raise RuntimeError("Stopwatch is not running.")

        current_time = pendulum.now()
        self._elapsed += current_time - self._start_time
        self._start_time = None

    def reset(self):
        """
        Reset the stopwatch to zero.
        """
        self._start_time = None
        self._elapsed = timedelta(0)

    @property
    def elapsed_time(self) -> timedelta:
        """
        Calculate the elapsed time since the stopwatch was started or last reset.
        """
        if self._start_time is None:
            return self._elapsed

        return self._elapsed + (pendulum.now() - self._start_time)

    def __str__(self) -> str:
        """
        String representation of the elapsed time.
        """
        elapsed = self.elapsed_time
        dummy_date = datetime(1, 1, 1) + elapsed
        return dummy_date.strftime(self.time_format)

    def _raise_comparison_error(self, other):
        raise TypeError(
            f"Can only compare to StopWatch, timedelta, int, or float, not {type(other)}."
        )

    def __eq__(self, other: Union["StopWatch", timedelta, int, float]):
        if isinstance(other, StopWatch):
            return self.elapsed_time == other.elapsed_time
        elif isinstance(other, timedelta):
            return self.elapsed_time == other
        elif isinstance(other, (int, float)):
            return self.elapsed_time.total_seconds() == other
        else:
            self._raise_comparison_error(other)

    def __ne__(self, other: Union["StopWatch", timedelta, int, float]):
        return not self == other

    def __lt__(self, other: Union["StopWatch", timedelta, int, float]):
        if isinstance(other, StopWatch):
            return self.elapsed_time < other.elapsed_time
        elif isinstance(other, timedelta):
            return self.elapsed_time < other
        elif isinstance(other, (int, float)):
            return self.elapsed_time.total_seconds() < other
        else:
            self._raise_comparison_error(other)

    def __le__(self, other: Union["StopWatch", timedelta, int, float]):
        return self < other or self == other

    def __gt__(self, other: Union["StopWatch", timedelta, int, float]):
        return not self <= other

    def __ge__(self, other: Union["StopWatch", timedelta, int, float]):
        return not self < other


if __name__ == "__main__":
    now = pendulum.now()
    one_hour_from_now = now.add(hours=1)

    print(now)
    print(one_hour_from_now)

    delta = one_hour_from_now - now
    print(delta)

    # Years, days, hours, minutes, seconds, microseconds
    print(delta.years)
    print(delta.days)
    print(delta.hours)
    print(delta.minutes)
    print(delta.seconds)
    print(delta.microseconds)
