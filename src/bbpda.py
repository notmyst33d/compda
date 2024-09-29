from .data import AttachmentType

def level_read(text, i, inc, dec):
    level = 0
    start = i
    while True:
        if text[i] == inc:
            level += 1
        if text[i] == dec:
            level -= 1
        if level == 0 or i >= len(text):
            break
        i += 1
    return i, text[start:i + 1]

def render_color(text):
    i = 0
    while True:
        i = text.find("[color=", i)
        if i == -1:
            break
        i, tag = level_read(text, i, "[", "]")
        color = tag[1:-1].split("=")[1]
        text = text.replace(tag, f"<span class=\"bb-color-{color}\">")

    text = text.replace("[/color]", "</span>")
    return text

def render_attachment(text, attachments):
    i = 0
    while True:
        i = text.find("[attachment=", i)
        if i == -1:
            break
        i, tag = level_read(text, i, "[", "]")
        attachment_info = tag[1:-1].split("=")[1].split(":")
        attachment_id = int(attachment_info[0][1:])
        attachment_name = attachment_info[1][:1]
        attachment = attachments[attachment_id]
        if attachment.type == AttachmentType.IMAGE:
            text = text.replace(tag, f"<img src=\"{attachment.url}\">")
        else:
            text = text.replace(tag, f"<span class=\"bold\">{attachment.url}</span>")

    return text

def render_spoiler(text):
    i = 0
    while True:
        i = text.find("[spoiler=", i)
        if i == -1:
            break
        i, tag = level_read(text, i, "[", "]")
        name = "=".join(tag[1:-1].split("=")[1:])
        text = text.replace(tag, f"<div class=\"bb-spoiler bb-spoiler-collapsed\">{name}</div><div class=\"bb-spoiler-content-collapsed\">")

    text = text.replace("[spoiler]", "<div class=\"bb-spoiler bb-spoiler-collapsed\">Спойлер</div><div class=\"bb-spoiler-content-collapsed\">")
    text = text.replace("[/spoiler]", "</div>")
    return text

def render(text, attachments):
    text = text.replace("&amp;#33;", "!")
    text = text.replace("&amp;#91;", "[")
    text = text.replace("&amp;#93;", "]")
    text = text.replace("&amp;#092;", "\\")
    text = text.replace("&amp;#036;", "$")
    text = text.replace("&amp;quot;", "\"")
    text = text.replace("&amp;lt;", "&lt;")
    text = text.replace("&amp;gt;", "&gt;")
    text = text.replace("&amp;hellip;", "...")
    text = text.replace("&quot;", "\"")
    text = text.replace("4pda.ru", "4pda.to")
    text = render_attachment(text, attachments)
    text = render_color(text)
    text = render_spoiler(text)
    return text
