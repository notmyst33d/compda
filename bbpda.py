# Very bad code ahead

from dataclasses import dataclass

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

def render(text):
    text = render_color(text)
    text = render_spoiler(text)
    return text

@dataclass
class Tag:
    name: str
    parameter: str
    content: str
    children: list

class Renderer:
    OPENER: str = "["
    CLOSER: str = "]"
    BREAKER: str = "/"

    i: int = 0

    def read_tag(self, text):
        start = self.i
        level = 0
        while True:
            if text[self.i] == self.OPENER:
                level += 1
            if text[self.i] == self.CLOSER:
                level -= 1

            if level == 0 or self.i >= len(text):
                break

            self.i += 1

        if self.i == len(text) - 1:
            return Tag(None, None, text, None)

        end = self.i

        header = text[start:end + 1]
        arguments = header[1:-1].split("=")
        name = arguments[0]
        parameter = ""
        if len(arguments) >= 2:
            parameter = "=".join(arguments[1:])

        self.i += 1
        content_start = self.i
        level = 1
        while True:
            if text[self.i] == self.OPENER:
                if text[self.i + 1] == self.BREAKER:
                    if text[self.i + 2:self.i + 2 + len(name)] == name:
                        level -= 1
                else:
                    if text[self.i + 1:self.i + 1 + len(name)] == name:
                        level += 1

            if level == 0 or self.i >= len(text):
                break

            self.i += 1

        content_end = self.i
        content = text[content_start:content_end]

        return Tag(name, parameter, content, [])

    def parse(self, text):
        self.i = 0
        while True:
            if self.i >= len(text) - 1:
                break

            if text[self.i] == self.OPENER:
                print(self.read_tag(text))

            self.i = self.i + 1

if __name__ == "__main__":
    #renderer = Renderer()
    #renderer.parse("[spoiler=[color=red]Важно[/color]][spoiler]Cool rendering[/spoiler][/spoiler][color=red]Yay[/color]")
    html = render("[spoiler=[color=red]Важно[/color]][spoiler]Cool rendering[/spoiler][/spoiler][color=red]Yay[/color]")
    print(html)
