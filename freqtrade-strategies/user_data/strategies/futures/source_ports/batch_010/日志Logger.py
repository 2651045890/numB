"""Deep semantic map of FMZ JavaScript strategy 日志Logger.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '日志Logger.md'
SOURCE_FEATURES = ['var ']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.']
ORIGINAL_JAVASCRIPT = '//var COLOR_ERROR = "#FF0000"\n//var COLOR_WARN = "#FF0000"\n//var COLOR_INFO = "#0000FF"\n//var COLOR_DEBUG = "#000000"\nvar LEVER_PATTERN = {\n  DEBUG: 0,\n  INFO: 1,\n  WARNING: 2,\n  ERROR: 3\n}\n//var loggerLever = [LEVER_PATTERN.DEBUG, LEVER_PATTERN.INFO, LEVER_PATTERN.WARNING, LEVER_PATTERN.ERROR][level]\n$.Error = function(msg) {\n  Log(\'[ERR] \', msg, \'#FF0000\')\n}\n\n$.Warn = function(msg) {\n  if(level <= LEVER_PATTERN.WARNING) {\n    Log(\'[WAR] \', msg, \'#FF0000\')\n  }  \n}\n\n$.Info = function(msg) {\n  if(level <= LEVER_PATTERN.INFO) {\n    Log(\'[INF] \', msg, \'#0000FF\')\n  }\n}\n\n$.Debug = function(msg) {\n  if(level <= LEVER_PATTERN.DEBUG) {\n    Log(\'[DBG] \', msg, \'#000000\')\n  }\n}\n\nfunction main() {\n  $.Error(\'this is error\')\n  $.Warn(\'this is warn\')\n  $.Info(\'this is info\')\n  $.Debug(\'this is debug\')\n}'

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
