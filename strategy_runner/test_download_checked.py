import unittest
import threading
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pandas as pd
from freqtrade.configuration import TimeRange
from freqtrade.data.history import history_utils
from download_checked import covered, install_checks, incremental_results, local_check_results


class CheckedDownloadTests(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame({'date': pd.date_range('2026-01-01', periods=4, freq='h', tz='UTC')})
        self.timerange = TimeRange.parse_timerange('20260101-20260101')
        self.timerange.stopts += 4 * 3600

    def test_prepend(self):
        self.assertTrue(covered(self.data, '1h', 'futures', self.timerange, True))
        self.assertFalse(covered(self.data.iloc[1:], '1h', 'futures', self.timerange, True))

    def test_missing_tail_gap_empty_and_funding(self):
        self.assertTrue(covered(self.data, '1h', 'futures', self.timerange, False))
        for data in (self.data.iloc[:-1], self.data.drop(1), self.data.iloc[:0]):
            self.assertFalse(covered(data, '1h', 'futures', self.timerange, False))
        self.assertFalse(covered(self.data, '1h', 'funding_rate', self.timerange, False))

    def test_open_range(self):
        self.assertTrue(covered(self.data, '1h', 'futures', TimeRange.parse_timerange('20260101-'), False,
                                datetime(2026, 1, 1, 4, 30, tzinfo=timezone.utc)))

    def test_incremental_workers_overlap_and_close_connections(self):
        barrier = threading.Barrier(3)
        lock = threading.Lock()
        clients = []
        active = 0
        peak = 0
        def factory(*args, **kwargs):
            client = Mock()
            with lock:
                clients.append(client)
            return client
        def process(pair, client):
            nonlocal active, peak
            with lock:
                active += 1
                peak = max(peak, active)
            barrier.wait(timeout=5)
            with lock:
                active -= 1
            if pair == 'B':
                raise RuntimeError('simulated failure')
            return False, True
        with patch('freqtrade.resolvers.ExchangeResolver.load_exchange', side_effect=factory), \
             patch('builtins.print'):
            results = dict(incremental_results(['A', 'B', 'C'], process, Mock(_config={}), 3))
        self.assertEqual(peak, 3)
        self.assertEqual(results['B'], (True, False))
        self.assertEqual(results['A'], (False, True))
        self.assertEqual(len(clients), 3)
        for client in clients:
            client.reload_markets.assert_called_once()
            client.close.assert_called_once()

    def test_local_checks_run_in_parallel(self):
        barrier = threading.Barrier(3)
        lock = threading.Lock()
        active = 0
        peak = 0

        def check(pair):
            nonlocal active, peak
            with lock:
                active += 1
                peak = max(peak, active)
            barrier.wait(timeout=5)
            with lock:
                active -= 1
            return pair.lower()

        self.assertEqual(
            {'A': 'a', 'B': 'b', 'C': 'c'},
            dict(local_check_results(['A', 'B', 'C'], check, 3)),
        )
        self.assertEqual(peak, 3)

    def run_phases(self, success=True):
        events = []
        handler = Mock()
        def load(pair, **kwargs):
            events.append(('check', pair, kwargs['timeframe']))
            return self.data if pair == 'OLD' or kwargs['timeframe'] == '1h' else self.data.iloc[:0]
        handler.ohlcv_load.side_effect = load
        def refresh(exchange, *, pairs, **kwargs):
            self.assertFalse(kwargs['prepend'])
            self.assertTrue(kwargs['no_parallel_download'])
            for tf in ('1h', '5m'):
                history_utils._download_pair_history(
                    pairs[0], timeframe=tf, candle_type='futures', data_handler=handler,
                    timerange=TimeRange.parse_timerange('20260101-'),
                )
            return []
        def download(pair, **kwargs):
            events.append(('download', pair, kwargs['timeframe']))
            return success
        with patch.object(history_utils, 'refresh_backtest_ohlcv_data', refresh), \
             patch.object(history_utils, '_download_pair_history', download), \
             patch('builtins.print') as output, \
             patch.dict('os.environ', {'DATA_CHECK_WORKERS': '1', 'DATA_DOWNLOAD_WORKERS': '1'}):
            install_checks()
            if success:
                history_utils.refresh_backtest_ohlcv_data(None, pairs=['OLD', 'PARTIAL'])
            else:
                with self.assertRaises(RuntimeError):
                    history_utils.refresh_backtest_ohlcv_data(None, pairs=['OLD', 'PARTIAL'])
            return events, str(output.call_args_list)

    def test_checks_all_before_first_download_then_updates_existing(self):
        events, logs = self.run_phases()
        self.assertEqual(events[:4], [('check', 'OLD', '1h'), ('check', 'OLD', '5m'),
                                      ('check', 'PARTIAL', '1h'), ('check', 'PARTIAL', '5m')])
        downloads = [e for e in events if e[0] == 'download']
        self.assertEqual(downloads, [('download', 'PARTIAL', '5m'), ('download', 'OLD', '1h'),
                                     ('download', 'OLD', '5m'), ('download', 'PARTIAL', '1h')])
        self.assertIn('已有全部所需数据 1 个，需要首次下载 1 个', logs)
        self.assertIn('所需数据：1h/futures，5m/futures', logs)
        self.assertIn('[开始下载]', logs)
        self.assertIn('时间范围', logs)
        self.assertIn('[下载处理完成]', logs)
        self.assertIn('耗时', logs)

    def test_failure_stops_before_incremental_phase(self):
        events, logs = self.run_phases(False)
        self.assertEqual([e for e in events if e[0] == 'download'], [('download', 'PARTIAL', '5m')])
        self.assertIn('失败 1 个', logs)


if __name__ == '__main__':
    unittest.main()
