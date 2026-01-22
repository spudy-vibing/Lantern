"""Tests for output formatting functions."""


from lantern.core.output import (
    format_bytes,
    format_latency,
    format_signal_strength,
    format_status,
    signal_bars,
)


class TestFormatLatency:
    """Tests for format_latency function."""

    def test_format_latency_low(self) -> None:
        """Test formatting low latency (< 20ms)."""
        result = format_latency(5.5)
        assert "5.5" in result
        assert "ms" in result
        assert "green" in result

    def test_format_latency_medium(self) -> None:
        """Test formatting medium latency (20-100ms)."""
        result = format_latency(75.0)
        assert "75.0" in result
        assert "ms" in result
        assert "yellow" in result

    def test_format_latency_high(self) -> None:
        """Test formatting high latency (>= 100ms)."""
        result = format_latency(250.0)
        assert "250.0" in result
        assert "ms" in result
        assert "red" in result


class TestFormatSignalStrength:
    """Tests for format_signal_strength function."""

    def test_excellent_signal(self) -> None:
        """Test formatting excellent signal (-50 dBm or better)."""
        result = format_signal_strength(-45)
        assert "-45" in result
        assert "dBm" in result
        assert "Excellent" in result
        assert "green" in result

    def test_good_signal(self) -> None:
        """Test formatting good signal (-50 to -60 dBm)."""
        result = format_signal_strength(-55)
        assert "-55" in result
        assert "Good" in result
        assert "green" in result

    def test_fair_signal(self) -> None:
        """Test formatting fair signal (-60 to -70 dBm)."""
        result = format_signal_strength(-65)
        assert "-65" in result
        assert "Fair" in result
        assert "yellow" in result

    def test_weak_signal(self) -> None:
        """Test formatting weak signal (< -70 dBm)."""
        result = format_signal_strength(-85)
        assert "-85" in result
        assert "Weak" in result
        assert "red" in result


class TestFormatBytes:
    """Tests for format_bytes function."""

    def test_format_bytes(self) -> None:
        """Test formatting various byte values."""
        assert "1.0 KB" in format_bytes(1024)
        assert "1.0 MB" in format_bytes(1024 * 1024)
        assert "1.0 GB" in format_bytes(1024 * 1024 * 1024)

    def test_format_small_bytes(self) -> None:
        """Test formatting small byte values."""
        result = format_bytes(512)
        assert "512" in result
        assert "B" in result

    def test_format_zero_bytes(self) -> None:
        """Test formatting zero bytes."""
        result = format_bytes(0)
        assert "0" in result


class TestFormatStatus:
    """Tests for format_status function."""

    def test_online_status(self) -> None:
        """Test formatting online status."""
        result = format_status(True)
        assert "Online" in result
        assert "green" in result

    def test_offline_status(self) -> None:
        """Test formatting offline status."""
        result = format_status(False)
        assert "Offline" in result
        assert "red" in result


class TestSignalBars:
    """Tests for signal_bars function."""

    def test_excellent_signal_bars(self) -> None:
        """Test signal bars for excellent signal."""
        result = signal_bars(-30)
        # Should have mostly filled bars
        assert "green" in result

    def test_weak_signal_bars(self) -> None:
        """Test signal bars for weak signal."""
        result = signal_bars(-90)
        # Should have mostly empty bars
        assert "dim" in result

    def test_max_bars(self) -> None:
        """Test custom max_bars."""
        result = signal_bars(-50, max_bars=3)
        # Should work with different bar counts
        assert result  # Just verify it doesn't crash
