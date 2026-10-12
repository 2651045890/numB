"""Deep semantic map of FMZ JavaScript strategy 爬取币安公告永续新上币和下架币.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '爬取币安公告永续新上币和下架币.md'
SOURCE_FEATURES = ['var ', 'Sleep(']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.']
ORIGINAL_JAVASCRIPT = "function main() {\n    var last_news = ''\n    while(true){\n        var html = HttpQuery('https://www.binance.com/en/support/announcement/c-49?navId=49')\n        if(html){\n            var news = html.match(/Launch .{0,40} Perpetual|Delist.{0,40}-\\d{1,2}/i)\n            if(news && last_news != news[0]){\n                Log(news[0],'@')\n                last_news = news[0]\n            }\n        }\n        Sleep(60*1000)\n    }\n}"

class FMZDeepPort:
    source_file = SOURCE_FILE
    source_features = SOURCE_FEATURES
    fidelity_notes = SOURCE_FIDELITY_NOTES
    javascript = ORIGINAL_JAVASCRIPT
    def run(self, adapter):
        runner = getattr(adapter, 'run_fmz_javascript', None)
        if runner is None:
            raise RuntimeError('This strategy needs an FMZ-compatible event/API adapter; refusing to invent OHLCV-only behavior.')
        return runner(self.javascript)
