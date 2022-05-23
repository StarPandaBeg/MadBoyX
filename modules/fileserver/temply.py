import re

class Temply:

    def __init__(self, base_dir="", extension="tpl"):
        self.base_dir = base_dir
        self.extension = extension

        self.clear()

    def load_template(self, name):
        path = f"{self.base_dir}/{name}.{self.extension}"
        try:
            with open(path, encoding='utf-8') as f:
                self.tpl = f.read()
                return True
        except:
            self.tpl = ""
            return False
        finally:
            self.data = {
                "blocks": {},
                "vars": {}
            }

    def set(self, var, value):
        self.data["vars"][var] = value

    def setBlock(self, block, state):
        self.data["blocks"][block] = state

    def compile(self, tplname):
        t = self.compiled.get(tplname, "")

        template = self.tpl
        for name, var in self.data["vars"].items():
            template = template.replace("{"+name+"}", var)

        for name, state in self.data["blocks"].items():
            r = rf"\[{name}\].*\[\/{name}\]"
            contents = re.findall(r, template, re.DOTALL)
            if state:
                template = template.replace(f"[{name}]", "")
                template = template.replace(f"[/{name}]", "")
            else:
                for c in contents:
                    template = template.replace(c, "")
        self.compiled[tplname] = t+template

    def get(self, tplname):
        return self.compiled.get(tplname, "")

    def clear(self):
        self.tpl = ""
        self.data = {
            "blocks": {},
            "vars": {}
        }
        self.compiled = {}