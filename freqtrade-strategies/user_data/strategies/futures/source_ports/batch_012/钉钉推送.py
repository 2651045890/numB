"""Source-preserving Python port envelope for 钉钉推送.md.

Original language: javascript.  This strategy is not PineScript and uses FMZ
exchange/event APIs or MyLanguage semantics.  It cannot be truthfully mapped to
the batch_001 candle PinePortBase engine without an event/order-book adapter.
The exact source is retained in ORIGINAL_SOURCE for a dedicated translation.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = "$.ddNotice = function(title, content) {\n    content = content == null ? title : content instanceof Array ? content.join('\\n') : content\n    HttpQuery(DING_URI, {\n        method: 'POST',\n        timeout: 3000,\n        data: JSON.stringify({\n            msgtype: 'markdown',\n            markdown: {\n                title: title,\n                text: content\n            }\n        })\n    }, null, 'Content-Type: application/json')\n}\n"
SOURCE_FILE = '钉钉推送.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ event/order-book adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
