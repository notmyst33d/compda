import bbcode
from datetime import datetime

def get_bbcode_parser(request, topic_id):
    port_str = ""
    if request.url.port:
        port_str = f":{request.url.port}"

    def render_size(tag_name, value, options, parent, context):
        sizes = {
            3: "24px",
            4: "32px",
        }
        size = sizes.get(options["size"], "16px")
        return f"<span style=\"font-size: {size};\">{value}</span>"

    def render_snapback(tag_name, value, options, parent, context):
        return f"<a href=\"{request.url.scheme}://{request.url.host}{port_str}/forum/index.php?showtopic={topic_id}&view=findpost&p={value}\"><img src=\"data:image/gif;base64,R0lGODlhCgAKAIAAAPTn6phiZSH5BAAAAAAALAAAAAAKAAoAAAIUjI8By2usYHwSJPWundH1vjXNlRQAOw==\"></a>"

    def render_mergetime(tag_name, value, options, parent, context):
        return datetime.fromtimestamp(int(value)).strftime("%d.%m.%y %H:%M")

    parser = bbcode.Parser(escape_html=False, replace_cosmetic=False, replace_links=False)
    del parser.recognized_tags["color"]
    del parser.recognized_tags["code"]
    del parser.recognized_tags["quote"]
    parser.add_formatter("size", render_size)
    parser.add_formatter("snapback", render_snapback)
    parser.add_formatter("mergetime", render_mergetime)
    parser.add_simple_formatter("img", "<img src=\"%(value)s\">")
    parser.add_simple_formatter("quote", "<div class=\"block-header\">Цитата</div><blockquote>%(value)s</blockquote>")
    parser.add_simple_formatter("code", "<div class=\"block-header\">Код</div><pre>%(value)s</pre>")

    return parser
